from unittest.mock import Mock

import pytest
from invenio_pidstore.models import PersistentIdentifier

from cd2h_repo_project.modules.records.marshmallow.json import LICENSES
from cd2h_repo_project.modules.records.views import (
    citation, extract_files, license_value_to_name, permissions_to_access_name,
    permissions_to_label_css, to_available_options
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


@pytest.fixture
def sort_options():
    return {
        "fieldA_desc": {
            "title": 'field A in desc.',
            "default_order": 'desc',
            "order": 2,
        },
        "fieldB": {
            "title": 'field B in desc.',
            "default_order": 'desc',
        },
        "fieldA_asc": {
            "title": 'field A in asc.',
            "default_order": 'asc',
            "order": 1,
        },
    }


def test_to_available_options_returns_options_dict(sort_options):
    available_options = to_available_options(sort_options)

    assert 'options' in available_options
    assert len(available_options['options'])


def test_to_available_options_generates_title_value_options(sort_options):
    available_options = to_available_options(sort_options)

    assert all(
        'title' in option and 'value' in option
        for option in available_options['options']
    )
    assert available_options['options'][0]['title'] == 'field B in desc.'
    assert available_options['options'][0]['value'] == 'fieldB'


def test_to_available_options_orders_by_order(sort_options):
    available_options = to_available_options(sort_options)

    assert available_options['options'][0]['title'] == 'field B in desc.'
    assert available_options['options'][1]['title'] == 'field A in asc.'
    assert available_options['options'][2]['title'] == 'field A in desc.'


@pytest.mark.parametrize("permissions, expected", [
        ("all_view", "success"),
        ("restricted_edit", "warning"),  # purposefully 'edit'
        ("private_edit", "danger")
    ])
def test_permissions_to_label_css(permissions, expected):
    assert permissions_to_label_css(permissions) == expected


@pytest.mark.parametrize("permissions, expected", [
        ("all_view", "Open Access"),
        ("all_edit", "Open Access"),
        ("restricted_edit", "Restricted Access"),
        ("private_view", "Private Access")
    ])
def test_permissions_to_access_name(permissions, expected):
    assert permissions_to_access_name(permissions) == expected


def test_nlm_citation_isnt_ordered_list_item(config, create_record):
    record = create_record()
    pid = PersistentIdentifier.get(
        record['_deposit']['pid']['type'],
        record['_deposit']['pid']['value'],
    )

    citation_str = citation(record, pid, style='national-library-of-medicine')

    assert not citation_str.startswith('1. ')
