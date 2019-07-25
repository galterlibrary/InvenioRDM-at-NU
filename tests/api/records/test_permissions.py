from unittest.mock import Mock

import pytest
from flask import request
from flask_principal import ActionNeed
from flask_security import current_user, login_user
from invenio_access import Permission
from invenio_files_rest.models import Bucket, ObjectVersion

from cd2h_repo_project.modules.records.api import RecordType
from cd2h_repo_project.modules.records.permissions import (
    CreateFilesPermission, CreatePermission, FilesPermission,
    ReadFilesPermission, RecordPermissions, edit_metadata_permission_factory,
    has_published, is_owner, view_permission_factory
)


@pytest.mark.parametrize(
    'user_id,owner_id,authenticated,expected',
    [
        (1, 1, True, True),    # authenticated owner
        (1, 1, False, False),  # unauthenticated owner
        (2, 1, True, False),   # stranger
    ]
)
def test_is_owner(user_id, owner_id, authenticated, expected):
    user = Mock(get_id=lambda: user_id, is_authenticated=authenticated)
    record = {'_deposit': {'owners': [owner_id]}}

    can = is_owner(user, record)

    assert can is expected


class TestFilesPermission(object):

    def test_factory_caches_on_request_in_request_ctx(
            self, create_record, request_ctx):
        record = create_record(published=False)
        bucket_id = record['_buckets']['deposit']
        bucket = Bucket.get(bucket_id)

        permission = FilesPermission.create(bucket, action='bucket-update')

        assert request.current_file_record == record

    def test_factory_create_update_action_returns_CreateFilesPermission(
            self, create_record, request_ctx):
        # Create/Add file == bucket-update
        record = create_record()
        bucket_id = record['_buckets']['deposit']
        bucket = Bucket.get(bucket_id)

        permission = FilesPermission.create(bucket, action='bucket-update')

        assert type(permission) == CreateFilesPermission

    def test_factory_read_action_returns_ReadFilesPermission(
            self, create_record, request_ctx):
        record = create_record()
        bucket_id = record['_buckets']['deposit']
        bucket = Bucket.get(bucket_id)
        # Read file == read on an ObjectVersion
        obj = ObjectVersion.create(bucket, 'foo.txt')

        permission = FilesPermission.create(obj, action='object-read')

        assert type(permission) == ReadFilesPermission

    def test_factory_for_unknown_obj_returns_superuser_permission(self):
        unknown_obj = {}

        permission = FilesPermission.create(unknown_obj, 'bucket-update')

        assert type(permission) == Permission
        assert ActionNeed('superuser-access') in permission.explicit_needs

    def test_factory_for_unknown_action_returns_superuser_permission(self):
        record = {'_deposit': {'owners': [1]}}

        permission = FilesPermission.create(record, 'unknown')

        assert type(permission) == Permission
        assert ActionNeed('superuser-access') in permission.explicit_needs


def test_create_files_permission_anonymous_user_not_allowed():
    record = {'type': RecordType.draft.value}  # content doesn't matter

    assert CreateFilesPermission(current_user, record).can() is False


@pytest.mark.parametrize(
    'user_id, owner_id, published, allowed',
    [
        # The below cases are mostly for drafts because it is more realistic
        # regular user - non-owned draft
        (1, 2, False, False),
        # regular user - non-owned published record (not common)
        (1, 2, True, False),
        # owner - owned draft (most common)
        (1, 1, False, True),
        # owner - owned published record
        (1, 1, True, True),
    ]
)
def test_create_files_permission_regular_user(
        user_id, owner_id, published, allowed,
        create_user, request_ctx):
    user = create_user({'id': user_id})  # user is automatically authenticated
    record = {
        '_deposit': {'owners': [owner_id]},
        'type': (
            RecordType.published.value if published else RecordType.draft.value
        )
    }

    assert CreateFilesPermission(user, record).can() is allowed


@pytest.mark.parametrize(
    'has_published, allowed',
    [
        # librarian - pure draft
        (False, False),
        # librarian - draft of published record
        (True, True),
    ]
)
def test_create_files_permission_librarian(
        has_published, allowed,
        create_record, create_user, request_ctx):
    user = create_user({'id': 1, 'provides': ['menrva-edit-published-record']})
    deposit = create_record(
        {'_deposit': {'owners': [2]}},
        published=False  # most common case
    )

    if has_published:
        deposit.publish()

    assert CreateFilesPermission(user, deposit).can() is allowed


@pytest.mark.parametrize(
    'has_published, allowed',
    [
        # SUPER_USER - pure draft
        (False, True),
        # SUPER_USER - draft of published record
        (True, True),
    ]
)
def test_create_files_permission_superuser(
        has_published, allowed,
        create_record, create_user, request_ctx):
    user = create_user({'id': 1, 'provides': ['superuser-access']})
    deposit = create_record(
        {'_deposit': {'owners': [2]}},
        published=False  # most common case
    )

    if has_published:
        deposit.publish()

    assert CreateFilesPermission(user, deposit).can() is allowed


@pytest.mark.parametrize(
    'user_id, logged_in, provides, owner_id, permissions, allowed',
    [
        # anonymous user - open access file
        (1, False, None, 1, RecordPermissions.ALL_VIEW, True),
        # anonymous user - restricted access file
        (1, False, None, 1, RecordPermissions.RESTRICTED_VIEW, False),
        # anonymous user - private access file
        (1, False, None, 1, RecordPermissions.PRIVATE_VIEW, False),
        # authenticated user - open access file
        (1, True, None, 2, RecordPermissions.ALL_VIEW, True),
        # authenticated user - restricted access file
        (1, True, None, 2, RecordPermissions.RESTRICTED_VIEW, True),
        # authenticated user non owner - private access file
        (1, True, None, 2, RecordPermissions.PRIVATE_VIEW, False),
        # authenticated user owner - private access file
        (1, True, None, 1, RecordPermissions.PRIVATE_VIEW, True),
        # super-user - private access file
        (3, True, 'superuser-access', 1, RecordPermissions.PRIVATE_VIEW, True),
        # See below for librarian case
    ])
def test_read_files_permission(
        user_id, logged_in, provides, owner_id, permissions, allowed,
        create_user, create_record, request_ctx):
    record = {
        '_deposit': {'owners': [owner_id]},
        'permissions': permissions,
        'type': RecordType.published.value
    }

    if logged_in:
        user = create_user({'id': user_id, 'provides': [provides]})
        login_user(user)  # makes user become current_user

    assert ReadFilesPermission(current_user, record).can() is allowed


@pytest.mark.parametrize(
    'permissions, published, allowed',
    [
        # unpublished record
        (RecordPermissions.RESTRICTED_VIEW, False, False),
        # published record
        (RecordPermissions.RESTRICTED_VIEW, True, True),
        # published private record
        (RecordPermissions.PRIVATE_VIEW, True, True),
    ])
def test_read_files_permission_for_librarians(
        permissions, published, allowed,
        create_user, create_record, request_ctx):
    # Covers librarians or anyone with 'menrva-view-published-record'
    user = create_user({'provides': ['menrva-view-published-record']})
    login_user(user)
    record = {
        'permissions': permissions,
        'type': (
            RecordType.published.value if published else RecordType.draft.value
        )
    }

    assert ReadFilesPermission(current_user, record).can() is allowed


@pytest.mark.parametrize(
    'user_id, logged_in, provides, owner_id, has_published, allowed',
    [
        # anonymous user - non-published draft
        # non-published for speed but same as published
        (1, False, None, 1, False, False),
        # authenticated user non-owner - non-published draft
        (2, True, None, 1, False, False),
        # authenticated user owner - non-published draft
        (1, True, None, 1, False, True),
        # user w/ published_record permission (librarian) - non-published draft
        (2, True, 'menrva-edit-published-record', 1, False, False),
        # user w/ published_record permission (librarian) - published draft
        (2, True, 'menrva-edit-published-record', 1, True, True),
        # super-user - non-published draft
        (3, True, 'superuser-access', 1, False, True),
    ]
)
def test_edit_metadata_permission_factory(
        user_id, logged_in, provides, owner_id, has_published, allowed,
        create_user, create_record, request_ctx):
    user = create_user({'id': user_id, 'provides': [provides]})
    deposit = create_record(
        {'_deposit': {'owners': [owner_id]}},
        published=False
    )

    if has_published:
        deposit.publish()

    if logged_in:
        login_user(user)

    # Invenio calls edit_metadata_permission_factory with `record` keyword
    permission = edit_metadata_permission_factory(record=deposit)

    assert permission.can() is allowed


@pytest.mark.parametrize(
    'logged_in, allowed',
    [
        # anonymous user
        (False, False),
        # authenticated user
        (True, True),
    ]
)
def test_create_permission_factory(
        logged_in, allowed, create_user, request_ctx):
    user = create_user()
    if logged_in:
        login_user(user)
    record = {}

    permission = CreatePermission.create(record)

    assert permission.can() == allowed


@pytest.mark.parametrize(
    'user_id, logged_in, provides, owner_id, permissions, allowed',
    [
        # anonymous user - open access record
        (1, False, None, 1, RecordPermissions.ALL_VIEW, True),
        # anonymous user - restricted access record
        (1, False, None, 1, RecordPermissions.RESTRICTED_VIEW, False),
        # anonymous user - private access record
        (1, False, None, 1, RecordPermissions.PRIVATE_VIEW, False),
        # authenticated user non-owner - restricted access record
        (2, True, None, 1, RecordPermissions.RESTRICTED_VIEW, True),
        # authenticated user non-owner - private access record
        (2, True, None, 1, RecordPermissions.PRIVATE_VIEW, False),
        # authenticated user owner - private access record
        (1, True, None, 1, RecordPermissions.PRIVATE_VIEW, True),
        # librarian - private access record
        (2, True, 'menrva-view-published-record', 1, RecordPermissions.PRIVATE_VIEW, True),  # noqa
        # super-user - private access record
        (2, True, 'superuser-access', 1, RecordPermissions.PRIVATE_VIEW, True),
        # See below for unpublished record
    ]
)
def test_view_permission_factory(
        user_id, logged_in, provides, owner_id, permissions, allowed,
        create_user, request_ctx):
    user = create_user({'id': user_id, 'provides': [provides]})
    if logged_in:
        login_user(user)
    record = {
        '_deposit': {'owners': [owner_id]},
        'permissions': permissions,
        'type': RecordType.published.value
    }

    permission = view_permission_factory(record)

    assert permission.can() == allowed


def test_view_permission_factory_unpublished_record():
    record = {'type': RecordType.draft.value}

    permission = view_permission_factory(record)

    assert permission.can() is False


@pytest.mark.parametrize(
    'record, expected',
    [
        ({}, True),
        ({'permissions': 'private_view'}, True),
        ({'permissions': 'restricted_view'}, False),
    ]
)
def test_is_private(record, expected):
    assert RecordPermissions.is_private(record) is expected


def test_has_published_for_published_record_should_return_true(create_record):
    published_record = create_record()

    assert has_published(published_record) is True
