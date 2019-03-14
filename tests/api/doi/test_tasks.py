"""Test Celery tasks."""

import json

import datacite
import pytest
from flask import url_for
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records_files.api import Record

from cd2h_repo_project.modules.doi.serializers import datacite_v41
from cd2h_repo_project.modules.doi.tasks import register_doi
from cd2h_repo_project.modules.records.minters import mint_record
from cd2h_repo_project.modules.records.resolvers import record_resolver
from utils import login_request_and_session


def test_register_doi_task_is_triggered_on_publish(
        config, create_record, mocker):
    orig_signal_trigger = config['DOI_REGISTER_SIGNALS']
    config['DOI_REGISTER_SIGNALS'] = True
    deposit = create_record(published=False)
    patched_delay = mocker.patch(
        'cd2h_repo_project.modules.records.api.register_doi.delay')

    deposit.publish()

    assert patched_delay.called

    config['DOI_REGISTER_SIGNALS'] = orig_signal_trigger


def test_register_doi_task_calls_succeeds(config, create_record, mocker):
    """Test successful doi task."""
    patched_client = mocker.patch(
        'cd2h_repo_project.modules.doi.tasks.DataCiteMDSClient')()
    orig_pidstore_datacite_doi_prefix = config['PIDSTORE_DATACITE_DOI_PREFIX']
    config['PIDSTORE_DATACITE_DOI_PREFIX'] = '10.5072'
    returned_doi = '10.5072/qwer-tyui'
    patched_client.metadata_post.return_value = 'OK ({})'.format(returned_doi)
    patched_indexer = mocker.patch(
        'cd2h_repo_project.modules.doi.tasks.RecordIndexer')()
    # Because publish() triggers the task, we need to perform some of the steps
    # of publish() without calling publish()
    record = create_record(published=False)
    mint_record(record.id, record)
    doi_pid = PersistentIdentifier.get(pid_type='doi', pid_value=record['id'])

    register_doi(record['id'])

    # Validate proper usage of DataCite API
    assert patched_client.metadata_post.called_with(
        datacite_v41.serialize(doi_pid, record)
    )
    assert patched_client.doi_post.called_with(
        returned_doi,
        'https://localhost:5000/records/{}'.format(record['id'])
    )

    # Validate DOI update
    doi_pid = PersistentIdentifier.get(pid_type='doi', pid_value=returned_doi)
    assert doi_pid.pid_value == returned_doi
    pid, record = record_resolver.resolve(str(record['id']))
    assert record['doi'] == returned_doi
    assert doi_pid.status == PIDStatus.REGISTERED

    # Validate indexing
    assert patched_indexer.index.called

    config['PIDSTORE_DATACITE_DOI_PREFIX'] = orig_pidstore_datacite_doi_prefix


def test_register_doi_task_retries_if_datacite_down(create_record, mocker):
    """Test register_doi task failing because of DataCite.

    Note that retries are done on another thread so only the initial call to
    retry can be tested.
    """
    patched_client = mocker.patch(
        'cd2h_repo_project.modules.doi.tasks.DataCiteMDSClient')()
    patched_retry = mocker.patch(
        'cd2h_repo_project.modules.doi.tasks.register_doi.retry')

    # Because publish() triggers the task, we need to perform some of the steps
    # of publish() without calling publish()
    record = create_record(published=False)
    mint_record(record.id, record)
    doi_pid = PersistentIdentifier.get(pid_type='doi', pid_value=record['id'])

    # Test HttpError
    patched_client.metadata_post.side_effect = datacite.errors.HttpError()

    register_doi(record['id'])

    number_retries = len(patched_retry.mock_calls)
    assert number_retries == 1

    # Test DataCiteError
    patched_client.metadata_post.side_effect = datacite.errors.DataCiteError()

    register_doi(record['id'])

    number_retries = len(patched_retry.mock_calls)
    assert number_retries == 2


def test_register_doi_task_doesnt_retry_if_other_error(create_record, mocker):
    """Test failing register_doi task because of us."""
    patched_client = mocker.patch(
        'cd2h_repo_project.modules.doi.tasks.DataCiteMDSClient')()
    patched_retry = mocker.patch(
        'cd2h_repo_project.modules.doi.tasks.register_doi.retry')

    # Because publish() triggers the task, we need to perform some of the steps
    # of publish() without calling publish()
    record = create_record(published=False)
    mint_record(record.id, record)
    doi_pid = PersistentIdentifier.get(pid_type='doi', pid_value=record['id'])

    patched_client.metadata_post.side_effect = Exception()

    with pytest.raises(Exception):
        register_doi(record['id'])

    number_retries = len(patched_retry.mock_calls)
    assert number_retries == 0
    assert not record['doi']


def test_register_doi_task_second_time_succeeds(config, create_record, mocker):
    patched_client = mocker.patch(
        'cd2h_repo_project.modules.doi.tasks.DataCiteMDSClient')()
    orig_pidstore_datacite_doi_prefix = config['PIDSTORE_DATACITE_DOI_PREFIX']
    config['PIDSTORE_DATACITE_DOI_PREFIX'] = '10.5072'
    patched_client.metadata_post.return_value = 'OK (10.5072/qwer-tyui)'
    patched_indexer = mocker.patch(
        'cd2h_repo_project.modules.doi.tasks.RecordIndexer')()
    # Because publish() triggers the task, we need to perform some of the steps
    # of publish() without calling publish()
    record = create_record(published=False)
    mint_record(record.id, record)
    doi_pid = PersistentIdentifier.get(pid_type='doi', pid_value=record['id'])

    register_doi(record['id'])
    register_doi(record['id'])  # Second time

    assert len(patched_client.metadata_post.mock_calls) == 2
    assert len(patched_client.doi_post.mock_calls) == 1

    config['PIDSTORE_DATACITE_DOI_PREFIX'] = orig_pidstore_datacite_doi_prefix
