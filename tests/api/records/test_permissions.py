from unittest import TestCase
from unittest.mock import Mock

import pytest
from flask import request
from flask_principal import ActionNeed
from flask_security import current_user, login_user
from invenio_access import Permission
from invenio_files_rest.models import Bucket

from cd2h_repo_project.modules.records.api import RecordType
from cd2h_repo_project.modules.records.permissions import (
    CreatePermission, CurrentUserFilesPermission, ReadFilesPermission,
    RecordPermissions, edit_metadata_permission_factory,
    files_permission_factory, has_published, is_owner, view_permission_factory
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


class TestCurrentUserFilesPermission(TestCase):
    """CurrentUserFilesPermission tests."""

    def test_create_for_bucket_update_action_returns_cls(self):
        record = {'_deposit': {'owners': [1]}}

        permission = CurrentUserFilesPermission.create(record, 'bucket-update')

        assert type(permission) == CurrentUserFilesPermission
        assert permission._can == is_owner

    def test_create_for_crazy_action_returns_admin_permission(self):
        record = {'_deposit': {'owners': [1]}}

        permission = CurrentUserFilesPermission.create(record, 'crazy')

        assert type(permission) == Permission
        assert ActionNeed('admin-access') in permission.explicit_needs


def test_files_permission_factory_for_unknown_obj_returns_admin_permission():
    unknown_obj = {}

    permission = files_permission_factory(unknown_obj, action='bucket-update')

    assert type(permission) == Permission
    assert ActionNeed('admin-access') in permission.explicit_needs


def test_files_permission_factory_for_bucket_obj_outside_request_returns_admin_permission(  # noqa
        create_record):
    create_record()
    unknown_obj = {}

    permission = files_permission_factory(unknown_obj, action='bucket-update')

    assert type(permission) == Permission
    assert ActionNeed('admin-access') in permission.explicit_needs


def test_files_permission_factory_for_bucket_obj_returns_ReadFilesPermission(
        create_record, request_ctx):
    record = create_record()
    bucket_id = record['_buckets']['deposit']
    bucket = Bucket.get(bucket_id)

    permission = files_permission_factory(bucket, action='bucket-update')

    assert type(permission) == ReadFilesPermission
    assert request.current_file_record


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
