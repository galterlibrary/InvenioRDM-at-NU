import uuid

import pytest
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from cd2h_repo_project.modules.records.minters import (
    mint_pids_for_deposit, mint_pids_for_record
)


def test_mint_pids_for_deposit_creates_depid_pid(config, db):
    object_uuid = uuid.uuid4()
    data = {}
    assert (
        PersistentIdentifier.query.filter_by(pid_type='depid').first() is None
    )

    mint_pids_for_deposit(object_uuid, data)

    _deposit = data['_deposit']
    assert _deposit['id']
    assert _deposit['status'] == 'draft'
    pid = PersistentIdentifier.get('depid', _deposit['id'])
    assert pid.object_uuid == object_uuid
    assert pid.status == PIDStatus.REGISTERED


def test_mint_pids_for_deposit_reserves_and_uses_recid_pid(config, db):
    object_uuid = uuid.uuid4()
    data = {}
    assert (
        PersistentIdentifier.query.filter_by(pid_type='recid').first() is None
    )

    mint_pids_for_deposit(object_uuid, data)

    recid_field = config['PIDSTORE_RECID_FIELD']
    assert data[recid_field]
    recid_pid = PersistentIdentifier.get('recid', data[recid_field])
    assert recid_pid.object_uuid is None
    assert recid_pid.status == PIDStatus.RESERVED
    _deposit = data['_deposit']
    depid_pid = PersistentIdentifier.get('depid', _deposit['id'])
    assert depid_pid.pid_value == recid_pid.pid_value


def test_mint_pids_for_record_creates_recid_pid(config, db):
    record_uuid = uuid.uuid4()
    data = {}
    assert (
        PersistentIdentifier.query.filter_by(pid_type='recid').first() is None
    )

    mint_pids_for_record(record_uuid, data)

    recid_value = data[config['PIDSTORE_RECID_FIELD']]
    assert recid_value
    pid = PersistentIdentifier.get('recid', recid_value)
    assert pid.object_uuid == record_uuid
    assert pid.status == PIDStatus.REGISTERED


def test_mint_pids_for_record_for_already_registered_recid_pid_raises_error(
        config, db):
    record_uuid = uuid.uuid4()
    data = {}
    mint_pids_for_record(record_uuid, data)

    with pytest.raises(AssertionError):
        mint_pids_for_record(record_uuid, data)


def test_mint_pids_for_record_creates_doi_pid(config, db):
    recid_field = config['PIDSTORE_RECID_FIELD']
    record_uuid = uuid.uuid4()
    data = {}
    assert (
        PersistentIdentifier.query.filter_by(pid_type='doi').first() is None
    )

    mint_pids_for_record(record_uuid, data)

    doi_value = data['doi']
    assert doi_value == ''
    pid = PersistentIdentifier.query.filter_by(pid_type='doi').first()
    assert pid.object_uuid == record_uuid
    assert pid.status == PIDStatus.NEW


def test_mint_pids_for_record_for_already_minted_doi_pid_raises_error(
        config, db):
    recid_field = config['PIDSTORE_RECID_FIELD']
    record_uuid = uuid.uuid4()
    data = {'doi': 'a value'}

    with pytest.raises(AssertionError):
        mint_pids_for_record(record_uuid, data)
