"""Local DOI minter."""

from flask import current_app
from invenio_pidstore.models import PersistentIdentifier, PIDStatus


def mint_record_doi(record_uuid, data):
    """Mint doi PersistentIdentifier in an initial New state.

    Because DOIs are minted by an external service, we create a PID for
    tracking purposes, but do not mark it as Registered NOR do we specify the
    final DOI value upfront. A unique and temporary doi value is put in the DB
    until the real (final) DOI value is minted and provided to us by the
    external service. For that reason, we don't pass that DOI value back in
    `data`.

    An asynchronous task will update this PID with results from the external
    service.

    A doi PersistentIdentifier can only be minted if the Record has an
    associated recid PersistentIdentifier and it has not been doi minted
    before.

    :param record_uuid: Record object uuid
    :param data: Record object as dict (or dict-like).
    :returns: doi PersistentIdentifier
    """
    recid_field = current_app.config['PIDSTORE_RECID_FIELD']
    assert recid_field in data and 'doi' not in data
    pid = PersistentIdentifier.create(
        'doi',
        data['id'],  # This is a purposefully unique but temporary value
        pid_provider='datacite',
        object_type='rec',
        object_uuid=record_uuid,
        status=PIDStatus.NEW,
    )
    data['doi'] = ''
    return pid
