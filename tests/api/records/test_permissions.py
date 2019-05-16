from unittest import TestCase
from unittest.mock import Mock

import pytest
from flask import request
from flask_principal import ActionNeed
from flask_security import login_user
from invenio_access import Permission
from invenio_files_rest.models import Bucket

from cd2h_repo_project.modules.records.permissions import (
    CurrentUserFilesPermission, RecordPermissions,
    edit_metadata_permission_factory, files_permission_factory, is_owner,
    view_permission_factory
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


def test_files_permission_factory_for_bucket_obj_outside_request_returns_CurrentUserFilesPermission(  # noqa
        create_record):
    create_record()
    unknown_obj = {}

    permission = files_permission_factory(unknown_obj, action='bucket-update')

    assert type(permission) == Permission
    assert ActionNeed('admin-access') in permission.explicit_needs


def test_files_permission_factory_for_bucket_obj_returns_CurrentUserFilesPermission(  # noqa
        create_record, request_ctx):
    record = create_record()
    bucket_id = record.model.json['_buckets']['deposit']
    bucket = Bucket.get(bucket_id)

    permission = files_permission_factory(bucket, action='bucket-update')

    assert type(permission) == CurrentUserFilesPermission
    assert permission._can == is_owner
    assert request.current_file_record


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
    # NOTE: edit_metadata_permission is always applied to a Deposit (draft)
    #       This Deposit may or may not have an associated Record (published)
    deposit = create_record(
        {'_deposit': {'owners': [owner_id]}},
        published=False
    )

    if has_published:
        deposit.publish()

    if logged_in:
        login_user(user)

    permission = edit_metadata_permission_factory(deposit)

    assert permission.can() is allowed


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
        (2, True, 'menrva-view', 1, RecordPermissions.PRIVATE_VIEW, True),
        # super-user - private access record
        (2, True, 'superuser-access', 1, RecordPermissions.PRIVATE_VIEW, True),
    ]
)
def test_view_permission_factory(
        user_id, logged_in, provides, owner_id, permissions, allowed,
        create_user, request_ctx):
    user = create_user({'id': user_id, 'provides': [provides]})
    if logged_in:
        login_user(user)
    record = {'_deposit': {'owners': [owner_id]}, 'permissions': permissions}

    permission = view_permission_factory(record)

    assert permission.can() == allowed
