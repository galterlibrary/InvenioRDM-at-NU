from unittest import TestCase
from unittest.mock import Mock

import pytest
from flask import request
from flask_principal import ActionNeed
from invenio_access import Permission
from invenio_files_rest.models import Bucket

from cd2h_repo_project.modules.records.permissions import (
    CurrentUserFilesPermission, files_permission_factory, is_owner
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
