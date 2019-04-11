import uuid

import pytest
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from cd2h_repo_project.modules.records.minters import mint_pids_for_record


def test_mint_pids_for_record_creates_recid_pid(config, db):
    rec_uuid = uuid.uuid4()
    data = {}
    assert (
        PersistentIdentifier.query.filter_by(pid_type='recid').first() is None
    )

    mint_pids_for_record(rec_uuid, data)

    recid_value = data[config['PIDSTORE_RECID_FIELD']]
    assert recid_value
    pid = PersistentIdentifier.get('recid', recid_value)
    assert pid.object_uuid == rec_uuid
    assert pid.status == PIDStatus.REGISTERED


def test_mint_pids_for_record_for_already_minted_recid_pid_raises_exception(
        config, db):
    rec_uuid = uuid.uuid4()
    data = {config['PIDSTORE_RECID_FIELD']: 'a value'}

    with pytest.raises(AssertionError):
        mint_pids_for_record(rec_uuid, data)


def test_mint_pids_for_record_creates_doi_pid(config, db):
    recid_field = config['PIDSTORE_RECID_FIELD']
    rec_uuid = uuid.uuid4()
    data = {}
    assert (
        PersistentIdentifier.query.filter_by(pid_type='doi').first() is None
    )

    mint_pids_for_record(rec_uuid, data)

    doi_value = data['doi']
    assert doi_value == ''
    pid = PersistentIdentifier.query.filter_by(pid_type='doi').first()
    assert pid.object_uuid == rec_uuid
    assert pid.status == PIDStatus.NEW


def test_mint_pids_for_record_for_already_minted_doi_pid_raises_exception(
        config, db):
    recid_field = config['PIDSTORE_RECID_FIELD']
    rec_uuid = uuid.uuid4()
    data = {'doi': 'a value'}

    with pytest.raises(AssertionError):
        mint_pids_for_record(rec_uuid, data)
