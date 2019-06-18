"""Test Celery tasks."""

import json

import datacite
import pytest
from elasticsearch.exceptions import RequestError
from flask import url_for
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from cd2h_repo_project.modules.doi.serializers import datacite_v41
from cd2h_repo_project.modules.doi.tasks import register_doi
from cd2h_repo_project.modules.records.api import Deposit
from cd2h_repo_project.modules.records.minters import mint_pids_for_record
from cd2h_repo_project.modules.records.permissions import RecordPermissions
from cd2h_repo_project.modules.records.resolvers import record_resolver
from utils import login_request_and_session


def test_register_doi_task_is_triggered_on_publish(
        config, create_record, mocker):
    original_doi_register_signals = config['DOI_REGISTER_SIGNALS']
    config['DOI_REGISTER_SIGNALS'] = True
    deposit = create_record(published=False)
    patched_delay = mocker.patch(
        'cd2h_repo_project.modules.doi.triggers.register_doi.delay')

    deposit.publish()

    assert patched_delay.called

    config['DOI_REGISTER_SIGNALS'] = original_doi_register_signals


@pytest.fixture
def patched_externalities(mocker):
    patched_client = mocker.patch(
        'cd2h_repo_project.modules.doi.tasks.DataCiteMDSClient')()
    returned_doi = '10.5072/qwer-tyui'
    patched_client.metadata_post.return_value = 'OK ({})'.format(returned_doi)
    patched_indexer = mocker.patch(
        'cd2h_repo_project.modules.doi.tasks.RecordIndexer')()

    return (patched_client, patched_indexer)


# TODO: Split this up in multiple tests
def test_register_doi_task_succeeds(
        config, create_record, patched_externalities):
    """Test successful doi task."""
    original_datacite_doi_prefix = config['PIDSTORE_DATACITE_DOI_PREFIX']
    config['PIDSTORE_DATACITE_DOI_PREFIX'] = '10.5072'
    original_doi_register_signals = config['DOI_REGISTER_SIGNALS']
    config['DOI_REGISTER_SIGNALS'] = False  # To be sure
    returned_doi = '10.5072/qwer-tyui'
    patched_client, patched_indexer = patched_externalities
    # NOTE: `create_record` does NOT trigger register_doi bc
    #       DOI_REGISTER_SIGNALS set to False
    record = create_record()
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
    assert doi_pid
    recid_pid, record = record_resolver.resolve(str(record['id']))
    depid_pid, deposit = Deposit.fetch_deposit(record)
    assert deposit['doi'] == returned_doi
    assert record['doi'] == returned_doi
    assert doi_pid.is_registered() and not doi_pid.is_new()
    # Validate indexing
    assert patched_indexer.index.called

    config['PIDSTORE_DATACITE_DOI_PREFIX'] = original_datacite_doi_prefix
    config['DOI_REGISTER_SIGNALS'] = original_doi_register_signals


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
    mint_pids_for_record(record.id, record)
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


def test_register_doi_task_doesnt_retry_if_indexing_error(
        create_record, mocker):
    """Test failing register_doi task because of us."""
    patched_client = mocker.patch(
        'cd2h_repo_project.modules.doi.tasks.DataCiteMDSClient')()
    patched_retry = mocker.patch(
        'cd2h_repo_project.modules.doi.tasks.register_doi.retry')
    # Because publish() triggers the task, we need to perform some of the steps
    # of publish() without calling publish()
    record = create_record(published=False)
    mint_pids_for_record(record.id, record)
    doi_pid = PersistentIdentifier.get(pid_type='doi', pid_value=record['id'])

    patched_client.metadata_post.side_effect = RequestError()

    register_doi(record['id'])

    number_retries = len(patched_retry.mock_calls)
    assert number_retries == 0
    assert not record['doi']


def test_register_doi_task_second_time_succeeds(
        config, create_record, patched_externalities):
    original_datacite_doi_prefix = config['PIDSTORE_DATACITE_DOI_PREFIX']
    config['PIDSTORE_DATACITE_DOI_PREFIX'] = '10.5072'
    patched_client, _ = patched_externalities
    # Because publish() triggers the task, we need to perform some of the steps
    # of publish() without calling publish()
    record = create_record(published=False)
    mint_pids_for_record(record.id, record)
    doi_pid = PersistentIdentifier.get(pid_type='doi', pid_value=record['id'])

    register_doi(record['id'])
    register_doi(record['id'])  # Second time

    assert len(patched_client.metadata_post.mock_calls) == 2
    assert len(patched_client.doi_post.mock_calls) == 2

    config['PIDSTORE_DATACITE_DOI_PREFIX'] = original_datacite_doi_prefix


@pytest.mark.parametrize('permissions, expected', [
    (RecordPermissions.ALL_VIEW, True),
    (RecordPermissions.PRIVATE_VIEW, False)
])
def test_register_doi_task_registers_landing_page_if_not_private(
        permissions, expected, config, create_record, patched_externalities):
    """Tests that private record is not minted a public DOI."""
    original_datacite_doi_prefix = config['PIDSTORE_DATACITE_DOI_PREFIX']
    config['PIDSTORE_DATACITE_DOI_PREFIX'] = '10.5072'
    original_doi_register_signals = config['DOI_REGISTER_SIGNALS']
    config['DOI_REGISTER_SIGNALS'] = False  # To be sure
    returned_doi = '10.5072/qwer-tyui'
    patched_client, _ = patched_externalities
    # NOTE: `create_record` does NOT trigger register_doi bc
    #       DOI_REGISTER_SIGNALS set to False
    record = create_record({'permissions': permissions})
    doi_pid = PersistentIdentifier.get(pid_type='doi', pid_value=record['id'])

    register_doi(record['id'])

    if expected:
        patched_client.doi_post.assert_called_with(
            returned_doi,
            'http://localhost:5000/records/{}'.format(record['id'])
        )
    else:
        patched_client.doi_post.assert_not_called()

    config['PIDSTORE_DATACITE_DOI_PREFIX'] = original_datacite_doi_prefix
    config['DOI_REGISTER_SIGNALS'] = original_doi_register_signals
