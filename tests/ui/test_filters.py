from unittest.mock import Mock

from cd2h_repo_project.modules.records.marshmallow.json import LICENSES
from cd2h_repo_project.modules.records.views import (
    extract_files, license_value_to_name
)


def test_extract_files_for_new_record_returns_empty_list():
    # A new record is a dict with no associated files
    new_record = {'_deposit': {'id': None}}

    files_dicts = extract_files(new_record)

    assert files_dicts == []


def test_extract_files_for_record_w_files_returns_files_dicts(appctx):
    record = Mock(files=[
        Mock(
            key='key',
            version_id='version_id',
            bucket_id='bucket_id',
            file=Mock(size='size', checksum='checksum')
        )
    ])

    files_dicts = extract_files(record)

    assert len(files_dicts) == 1
    assert files_dicts[0] == {
        'key': 'key',
        'version_id': 'version_id',
        'checksum': 'checksum',
        'size': 'size',
        'completed': True,
        'progfiles_dictss': 100,
        'links': {'self': '/api/files/bucket_id/key?versionId=version_id'}
    }


def test_license_value_to_name_for_known_license_returns_name():
    license_value = 'mit-license'

    name = license_value_to_name(license_value)

    assert name == 'MIT License'


def test_license_value_to_name_for_unknown_license_returns_none():
    license_value = None

    name = license_value_to_name(license_value)

    assert name is None