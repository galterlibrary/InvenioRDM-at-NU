"""Permission framework for Records."""

from flask import request
from flask_principal import ActionNeed
from flask_security import current_user
from invenio_access import Permission
from invenio_deposit.scopes import write_scope
from invenio_deposit.utils import check_oauth2_scope
from invenio_files_rest.models import Bucket, MultipartObject, ObjectVersion
from invenio_records_files.models import RecordsBuckets

from cd2h_repo_project.modules.records.api import (
    FileObject, Record, RecordType
)
from cd2h_repo_project.utils import get_identity

# Need instances #
# These are granular badge-like permissions that can be assigned via the cli
menrva_view_published_record = ActionNeed('menrva-view-published-record')
"""Permission to view any published record."""
menrva_edit_published_record = ActionNeed('menrva-edit-published-record')
"""Permission to edit published record ONLY."""
menrva_edit = ActionNeed('menrva-edit')
"""Permission to edit published OR draft record."""


class RecordPermissions(object):
    """Encompass all RecordPermissions.

    # TODO: We eventually want to have:
    actions = ['view_metadata', 'edit_metadata', 'view_files', 'edit_files']
    targets = ['all', 'logged_users', '<any specific users>', '<organization>']
    """

    ALL_VIEW = 'all_view'
    RESTRICTED_VIEW = 'restricted_view'
    PRIVATE_VIEW = 'private_view'

    @classmethod
    def get_values(cls):
        """Return permission string values.

        WARNING: This list must be compatible with `permissions` values from
                 modules/records/static/json/records/deposit_form.json
                 modules/records/jsonschemas/records/record-v0.1.0.json
        """
        return [cls.ALL_VIEW, cls.RESTRICTED_VIEW, cls.PRIVATE_VIEW]

    @classmethod
    def is_private(cls, record):
        """Returns if record is private or not.

        Abstracts away permissions implementation and defaults to private if
        no permissions.
        """
        return record.get('permissions', 'private_').startswith('private_')


class CreatePermission(object):
    """Gate to allow or not creation of a draft."""

    def __init__(self, user, draft):
        """Constructor."""
        self.user = user
        self.draft = draft

    @classmethod
    def create(cls, record):
        """Factory.

        `record` must be kept as argument because record=record is used by
        external module.
        """
        return cls(current_user, record)

    def can(self):
        """Returns boolean if permission valid."""
        return (
            self.user and self.user.is_authenticated
        )


class ViewPermission(object):
    """Gate to allow or not view of a published record.

    NOTE: This is a wider and simpler permission net; it is used for viewing
          metadata and files. It should be set in config.py for UI and API.
    """

    def __init__(self, user, published_record):
        """Constructor."""
        self.user = user
        self.published_record = published_record

    def can(self):
        """Return boolean if permission valid."""
        # Enforce the fact that this is only for published record.
        return RecordType.is_published(self.published_record) and (
            is_open_access(self.published_record) or
            has_restricted_access(self.user, self.published_record) or
            is_owner(self.user, self.published_record) or
            Permission(menrva_view_published_record).allows(
                get_identity(self.user)
            )
            # NOTE: by default any Permission has a super-user Need
        )


def view_permission_factory(record):
    """Returns ViewPermission object.

    `record` parameter must be kept because record=record is used externally.
    """
    return ViewPermission(current_user, record)


class EditMetadataPermission(object):
    """Gate to allow or not update of a record metadata.

    We reuse Zenodo's pattern, while trying to simplify it and make it more
    explicit.

    NOTE: It is passed a record (draft OR published).
    NOTE: This is currently used for metadata and files i.e. editing a deposit.
    TODO: Use this just for metadata.
    """

    def __init__(self, user, record):
        """Constructor.

        :param user: typically the current_user.
        :param record: a draft (unpublished record) or published record.
        """
        self.user = user
        self.record = record

    def can(self):
        """Return boolean if permission valid."""
        identity = get_identity(self.user)
        return (
            is_owner(self.user, self.record) or
            (
                Permission(menrva_edit_published_record).allows(identity) and
                has_published(self.record)
            ) or
            Permission(menrva_edit).allows(identity)
            # NOTE: by default any Permission has a super-user Need
        )


def edit_metadata_permission_factory(record):
    """Returns EditMetadataPermission object.

    Invenio (invenio_records_rest/views.py) passes the draft via a keyword
    argument: `record=record`, so the parameter must be named `record`.
    """
    return EditMetadataPermission(current_user, record)


# User - Record permissions checks


def is_owner(user, record):
    """Check if user is an owner of the record."""
    user_id = int(user.get_id()) if user and user.is_authenticated else None
    return user_id in record.get('_deposit', {}).get('owners', [])


def has_restricted_access(user, record):
    """Returns True if record is restricted and user is authenticated."""
    return (
        record.get('permissions', '').startswith('restricted_') and
        user and user.is_authenticated
    )


# Record permission checks


def is_open_access(record):
    """Returns True if permissions subject(s) is anyone (all)."""
    return record.get('permissions', '').startswith('all_')


def has_published(record):
    """Returns True if the record has any published record.

    NOTE: the published record might be itself.

    For efficiency, we don't hit the database.
    """
    pid = record.get('_deposit', {}).get('pid', {})
    return bool(pid.get('value')) and bool(pid.get('type'))


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


class CreateFilesPermission(EditMetadataPermission):
    """Gate to allow creation of files for a record."""

    pass


class ReadFilesPermission(ViewPermission):
    """Gate to allow reading of files for a record.

    TODO: ViewPermission -> ReadRecordPermission
    TODO: Differentiate between {ReadRecord,ReadFiles}Permission
    """

    pass


class FilesPermission(object):
    """Gates to allow or not files actions.

    This dynamically generates the permissions required to access
    `obj`. `check_permission` is typically used on the returned value to
    assess if the permissions are met.
    """

    actions = [
        'bucket-read',
        'bucket-read-versions',
        'bucket-update',
        'bucket-listmultiparts',
        'object-read',  # Read/Download a file action
        'object-read-version',
        'object-delete',
        'object-delete-version',
        'multipart-read',
        'multipart-delete',
    ]

    @classmethod
    def create(cls, obj, action):
        """Create an <Action>FilesPermission for record associated with `obj`.

        For now it defaults to ReadFilesPermission for all actions.

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
        if not bucket_id:
            # Don't think this conditional should be hit
            return Permission(ActionNeed('superuser-access'))

        # WARNING: invenio-records-files implies a one-to-one relationship
        #          between Record and Bucket, but does not enforce it
        #          "for better future" the invenio-records-files code says
        record_bucket = \
            RecordsBuckets.query.filter_by(bucket_id=bucket_id).one_or_none()
        if not record_bucket:
            return Permission(ActionNeed('superuser-access'))

        record_metadata = record_bucket.record
        record = Record(record_metadata.json, model=record_metadata)

        # "Cache" the file's record in the request context
        if record and request:
            setattr(request, 'current_file_record', record)

        if record:
            # TODO: Differentiate between actions
            if action in cls.actions:
                if '-read' in action:
                    return ReadFilesPermission(current_user, record)
                elif '-update' in action:
                    return CreateFilesPermission(current_user, record)

        return Permission(ActionNeed('superuser-access'))


def files_permission_factory(obj, action=None):
    """Factory function for `FilesPermission.create` (equivalent).

    Kept in case `FilesPermission.create` can't be used in configuration
    anymore. This could happen if we get circular dependencies.
    """
    return FilesPermission.create(obj, action)
