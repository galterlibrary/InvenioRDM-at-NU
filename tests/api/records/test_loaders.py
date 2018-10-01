from unittest.mock import Mock

from cd2h_repo_project.modules.records.marshmallow.json import (
    MetadataSchemaV1, RecordSchemaV1
)


def test_RecordSchemaV1_load_for_empty_json_contains_schema():
    unmarshalled_record = RecordSchemaV1().load({})

    assert not unmarshalled_record.errors
    assert unmarshalled_record.data == {
        '$schema': ('https://cd2hrepo.galter.northwestern.edu/'
                    'schemas/records/record-v0.1.0.json'),
    }


def test_RecordSchemaV1_load_for_valid_json_removes_metadata_envelope():
    serialized_record = {
        'metadata': {
            'author': 'An author', 'description': 'A description',
            'title': 'A title'
        }
    }

    unmarshalled_record = RecordSchemaV1().load(serialized_record)

    assert not unmarshalled_record.errors
    loaded_record = unmarshalled_record.data
    assert 'metadata' not in loaded_record
    assert loaded_record['title'] == 'A title'
    assert loaded_record['description'] == 'A description'
    assert loaded_record['author'] == 'An author'


def test_RecordSchemaV1_load_for_invalid_json_returns_errors():
    serialized_record = {'foo': 'bar'}

    unmarshalled_record = RecordSchemaV1().load(serialized_record)

    assert 'foo' in unmarshalled_record.errors
    assert not unmarshalled_record.data


def test_MetadataSchemaV1_load_for_invalid_json_returns_errors():
    # Invalid key and missing keys
    serialized_record = {'foo': 'bar'}

    unmarshalled_record = MetadataSchemaV1().load(serialized_record)

    assert 'foo' not in unmarshalled_record.errors  # marshmallow does not care
    assert 'title' in unmarshalled_record.errors
    assert 'description' in unmarshalled_record.errors
    assert 'author' in unmarshalled_record.errors
    assert not unmarshalled_record.data

    # Empty required key
    serialized_record = {
        'title': None,
        'description': 'A description',
        'author': 'An author'
    }

    unmarshalled_record = MetadataSchemaV1().load(serialized_record)

    assert 'title' in unmarshalled_record.errors
    # Partial validation is allowed
    loaded_record = unmarshalled_record.data
    assert loaded_record['description'] == 'A description'
    assert loaded_record['author'] == 'An author'

    # Value too short
    serialized_record = {
        'title': 'A title',
        'description': 'A ',
        'author': 'An author'
    }

    unmarshalled_record = MetadataSchemaV1().load(serialized_record)

    assert 'description' in unmarshalled_record.errors
    loaded_record = unmarshalled_record.data
    assert loaded_record['title'] == 'A title'
    assert loaded_record['author'] == 'An author'
