"""Permission for bucket/files interaction."""

from flask import current_app, request, session
from flask_principal import ActionNeed
from flask_security import current_user
from invenio_access import Permission
from invenio_files_rest.models import Bucket, MultipartObject, ObjectVersion
from invenio_records.api import Record
from invenio_records_files.api import FileObject
from invenio_records_files.models import RecordsBuckets


def files_permission_factory(obj, action=None):
    """
    Permission for files.

    This dynamically generates the permissions required to access
    `obj`. `check_permission` is typically used on the returned value to
    assess if the permissions are met.

    For now, it covers:
    - Deposit Owner has permission to add a file to the bucket associated with
      the record (at creation time) i.e. `obj` is a Bucket.

    TODO: Add/modify the file permissions based on our needs over time.

    Adapted from https://github.com/zenodo/zenodo
    """
    # Extract bucket id
    bucket_id = None
    if isinstance(obj, Bucket):
        bucket_id = str(obj.id)
    elif isinstance(obj, ObjectVersion):
        bucket_id = str(obj.bucket_id)
    elif isinstance(obj, MultipartObject):
        bucket_id = str(obj.bucket_id)
    elif isinstance(obj, FileObject):
        bucket_id = str(obj.bucket_id)

    # Retrieve record
    if bucket_id is not None:
        # WARNING: invenio-records-files implies a one-to-one relationship
        #          between Record and Bucket, but does not enforce it
        #          "for better future" the invenio-records-files code says
        record_bucket = \
            RecordsBuckets.query.filter_by(bucket_id=bucket_id).one_or_none()
        if record_bucket is not None:
            record = Record.get_record(record_bucket.record_id)

            # "Cache" the file's record in the request context
            if record and request:
                setattr(request, 'current_file_record', record)

            if record:
                return CurrentUserFilesPermission.create(record, action)

    return Permission(ActionNeed('admin-access'))


class CurrentUserFilesPermission(object):
    """Current user's permission for files in deposit / record.

    This Permission-style class presents an interface that invenio-files-rest
    expects.
    """

    update_actions = [
        'bucket-read',
        'bucket-read-versions',
        'bucket-update',
        'bucket-listmultiparts',
        'object-read',
        'object-read-version',
        'object-delete',
        'object-delete-version',
        'multipart-read',
        'multipart-delete',
    ]

    def __init__(self, record, can_implementation):
        """Initialize a file permission object."""
        self.record = record
        self._can = can_implementation

    def can(self):
        """Determine access for the current_user.

        CurrentUserFilesPermission respects the notion that admins are
        all-powerful.
        """
        return (
            self._can(current_user, self.record) or
            Permission(ActionNeed('admin-access')).can()
        )

    @classmethod
    def create(cls, record, action):
        """Create a CurrentUserFilesPermission.

        Create a CurrentUserFilesPermission for `record` based on
        `action`.
        """
        if action in cls.update_actions:
            return cls(record, is_owner)
        else:
            return Permission(ActionNeed('admin-access'))


# User - Record permissions checks


def is_owner(user, record):
    """Check if user is an owner of the record."""
    user_id = int(user.get_id()) if user.is_authenticated else None
    return (
        # TODO: is this first condition needed?
        user_id in record.get('owners', []) or
        user_id in record.get('_deposit', {}).get('owners', [])
    )
