"""CD2H Record minters."""

from flask import current_app
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.providers.recordid import RecordIdProvider

from cd2h_repo_project.modules.doi.minters import mint_doi_pid


def mint_pids_for_record(record_uuid, data):
    """Record PersistentIdentifiers minter.

    Mints:
        recid PersistentIdentifier
        doi PersistentIdentifier

    :param record_uuid: Record object uuid.
    :param data: Record object as dict (or dict-like).
    :returns: recid PersistentIdentifier
    """
    pid = mint_recid_pid(record_uuid, data)
    mint_doi_pid(record_uuid, data)
    return pid


def mint_recid_pid(record_uuid, data):
    """Mint recid PersistentIdentifier.

    A recid PersistentIdentifier can only be minted if the Record has not
    been recid minted before.

    :param record_uuid: Record object uuid
    :param data: Record object as dict (or dict-like).
    :returns: recid PersistentIdentifier
    """
    recid_field = current_app.config['PIDSTORE_RECID_FIELD']
    assert recid_field not in data
    pid = RecordIdProvider.create(
        object_type='rec', object_uuid=record_uuid).pid
    data[recid_field] = int(pid.pid_value)
    return pid
