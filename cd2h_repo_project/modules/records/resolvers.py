"""CD2H Record resolver."""

from invenio_pidstore.resolver import Resolver
from invenio_records_files.api import Record

record_resolver = Resolver(
    pid_type='recid', object_type='rec', getter=Record.get_record
)
"""'recid'-PID resolver for published Records."""
