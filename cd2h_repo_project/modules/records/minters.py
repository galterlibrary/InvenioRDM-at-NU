"""CD2H Record minters."""

from flask import current_app
from invenio_pidstore.models import (
    PersistentIdentifier, PIDStatus, RecordIdentifier
)
from invenio_pidstore.providers.base import BaseProvider

from cd2h_repo_project.modules.doi.minters import mint_doi_pid


class MenrvaRecordPIDProvider(BaseProvider):
    """Logic for MenrvaRecord PersistentIdentifier creation.

    Groups together and abstracts the logic around PersistentIdentifier
    creation for published Menrva records.
    """

    pid_type = 'recid'
    """Type of persistent identifier."""

    @classmethod
    def create(cls, **kwargs):
        """Constructor to use."""
        return super(MenrvaRecordPIDProvider, cls).create(
            # TODO: Settle on pid_value. See #350
            pid_value=str(RecordIdentifier.next()),
            object_type='rec',
            **kwargs
        )


def mint_pids_for_deposit(deposit_uuid, data):
    """Deposit PersistentIdentifier minter.

    Reserves published Record PersistentIdentifier so that Deposit
    PresistentIdentifier can share value.
    """
    recid_pid = MenrvaRecordPIDProvider.create(status=PIDStatus.RESERVED).pid
    # TODO: revisit int() if type of pid_value changes
    recid_field = current_app.config['PIDSTORE_RECID_FIELD']
    data[recid_field] = int(recid_pid.pid_value)

    depid = PersistentIdentifier.create(
        'depid',
        str(recid_pid.pid_value),
        object_type='rec',
        object_uuid=deposit_uuid,
        status=PIDStatus.REGISTERED,
    )

    data['_deposit'] = {
        'id': depid.pid_value,
        'status': 'draft',  # because expected by invenio-deposit
    }

    return depid


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

    if recid_field in data:
        # PersistentIdentifier previously reserved
        recid_pid = PersistentIdentifier.get('recid', data[recid_field])
        assert recid_pid.status == PIDStatus.RESERVED
        recid_pid.assign('rec', record_uuid)
        recid_pid.register()
    else:
        # Not already associated recid PersistendIdentifier
        recid_pid = (
            MenrvaRecordPIDProvider
            .create(
                object_uuid=record_uuid,
                status=PIDStatus.REGISTERED
            )
            .pid
        )
        # TODO: revisit int() if type of pid_value changes
        data[recid_field] = int(recid_pid.pid_value)

    return recid_pid
