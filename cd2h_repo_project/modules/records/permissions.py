"""Permission framework for Records."""

from flask import request
from flask_principal import ActionNeed
from flask_security import current_user
from invenio_access import Permission
from invenio_deposit.scopes import write_scope
from invenio_deposit.utils import check_oauth2_scope
from invenio_files_rest.models import Bucket, MultipartObject, ObjectVersion
from invenio_records_files.models import RecordsBuckets

from cd2h_repo_project.modules.records.api import FileObject, Record
from cd2h_repo_project.utils import get_identity

# Need instances #
# These are granular badge-like permissions that can be assigned via the cli
cd2h_edit_metadata = ActionNeed('cd2h-edit-metadata')
"""Permission to edit ANY record's metadata."""


class CurrentUserFilesPermission(object):
    """Current user's permission for files in deposit / record.

    This Permission-style class presents an interface that invenio-files-rest
    expects.

    TODO: Refactor this for consistency with other approaches.
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


class RecordPermissions(object):
    """Encompass all RecordPermissions.

    # TODO: We eventually want to have:
    actions = ['view_metadata', 'edit_metadata', 'view_files', 'edit_files']
    targets = ['all', 'logged_users', '<any specific users>', '<organization>']
    """

    @classmethod
    def get_values(cls):
        """Return permission string values.

        WARNING: This list must be compatible with `permissions` values from
                 modules/records/static/json/records/deposit_form.json
                 modules/records/jsonschemas/records/record-v0.1.0.json
        """
        return ['all_view', 'restricted_view', 'private_view']


class EditMetadataPermission(object):
    """Gate to allow or not update of a record metadata.

    We reuse Zenodo's pattern, while trying to simplify it and make it more
    explicit.
    """

    def __init__(self, user, record):
        """Constructor."""
        self.user = user
        self.record = record

    def can(self):
        """Return boolean if permission valid."""
        identity = get_identity(self.user)
        return (
            is_owner(self.user, self.record) or
            Permission(cd2h_edit_metadata).allows(identity)
            # NOTE: by default any Permission has a super-user Need
        )


def edit_metadata_permission_factory(record):
    """Returns EditMetadataPermission object."""
    return EditMetadataPermission(current_user, record)


# User - Record permissions checks


def is_owner(user, record):
    """Check if user is an owner of the record."""
    user_id = int(user.get_id()) if user and user.is_authenticated else None
    return user_id in record.get('_deposit', {}).get('owners', [])


# TODO: Enable when working on out-of-browser API interface
# def check_oauth2_write_scope(can_method):
#     """Wraps a can_method with a check for write-ability.

#     This is done to cover API permission as well.

#     :param can_method: Permission check function that accepts a record and
#                        returns a boolean.
#     :returns: A :class:`flask_principal.Permission` factory.
#     """

#     return check_oauth2_scope(can_method, write_scope.id)

# def deposit_update_permission_factory(record=None):
#     """Deposit update permission factory.

#     Since Deposit API "actions" (eg. publish, discard, etc) are considered
#     part
#     of the "update" action, request context (if present) has to be used in
#     order to figure out if this is an actual "update" or API action.
#     """
#     # TODO: The `need_record_permission` decorator of
#     # `invenio_deposit.views.rest.DepositActionResource.post` should be
#     # modified in order to be able to somehow provide a different permission
#     # factory for the various Deposit API actions and avoid hacking our way
#     # around to determine if it's an "action" or "update".
#     if request and request.endpoint == 'invenio_deposit_rest.depid_actions':
#         action = request.view_args.get('action')
#         if action in DepositPermission.protected_actions:
#             return DepositPermission.create(record=record, action=action)
#     return DepositPermission.create(record=record, action='update')
