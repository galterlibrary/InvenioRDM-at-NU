"""Test record form i.e. marshmallow schema is configured as expected."""

from copy import deepcopy

import pytest

from cd2h_repo_project.modules.records.marshmallow.json import (
    AuthorSchemaV1, MetadataSchemaV1, RecordSchemaV1, ResourceTypeSchemaV1
)


@pytest.fixture
def create_input_metadatav1():
    """Factory pattern for the input to the marshmallow.json.MetadataSchemaV1.
    """
    def _create_input_metadatav1(data={}):
        data_to_use = {
            'title': 'A title',
            'authors': [
                {
                    'first_name': 'An',
                    'last_name': 'author'
                }
            ],
            'description': 'A description',
            'resource_type': {
                'general': 'other',
                'specific': 'other'
            },
            'license': 'mit-license',
            'permissions': 'all_view',
        }
        data_to_use.update(data)
        return data_to_use

    return _create_input_metadatav1


@pytest.fixture
def create_input_record(create_input_metadatav1):
    """Factory pattern for an API input Record.

    The returned dict is the input to the marshmallow loader used by the API.
    """
    def _create_input_record(data=None):
        data = deepcopy(data) if data else {}
        data_to_use = {
            'metadata': create_input_metadatav1(data.pop('metadata', {}))
        }
        data_to_use.update(data)
        return data_to_use

    return _create_input_record


class TestRecordSchemaV1(object):
    def test_load_for_empty_json_contains_schema(self, appctx):
        unmarshalled_record = RecordSchemaV1().load({})

        assert not unmarshalled_record.errors
        assert unmarshalled_record.data == {
            '$schema': (
                'https://localhost:5000/schemas/records/record-v0.1.0.json'
            )
        }

    def test_load_for_valid_json_removes_metadata_envelope(
            self, create_input_record):
        input_record = create_input_record()

        unmarshalled_record = RecordSchemaV1().load(input_record)

        assert not unmarshalled_record.errors
        loaded_record = unmarshalled_record.data
        assert 'metadata' not in loaded_record

    def test_load_for_invalid_json_returns_errors(self):
        input_record = {'foo': 'bar'}

        unmarshalled_record = RecordSchemaV1().load(input_record)

        assert 'foo' in unmarshalled_record.errors
        assert not unmarshalled_record.data


class TestMetadataSchemaV1(object):

    def test_extra_key_is_ignored(self, create_input_metadatav1):
        serialized_record = create_input_metadatav1({'foo': 'bar'})

        unmarshalled_record = MetadataSchemaV1().load(serialized_record)
        loaded_record = unmarshalled_record.data

        # marshmallow does not care about additional keys
        assert 'foo' not in unmarshalled_record.errors
        assert 'foo' not in loaded_record

    def test_missing_keys_return_errors(self):
        serialized_record = {'foo': 'bar'}

        unmarshalled_record = MetadataSchemaV1().load(serialized_record)

        required_keys = [
            'title', 'description', 'authors', 'resource_type', 'license',
            'permissions'
        ]
        assert set(unmarshalled_record.errors.keys()) == set(required_keys)
        assert (
            unmarshalled_record.errors['title'] ==
            ['Missing data for required field.']
        )

    def test_authors_loaded(self, create_input_metadatav1):
        authors = [
            {
                'first_name': 'John',
                'middle_name': 'Jacob',
                'last_name': 'Smith'
            },
            {
                'first_name': 'Jane',
                'middle_name': 'Janet',
                'last_name': 'Doe',
                'full_name': 'Doe, Jane J.'  # Should be overwritten
            }
        ]
        serialized_record = create_input_metadatav1({
            'authors': authors
        })

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record)
        deserialized_metadata = unmarshalled_metadata.data

        assert not unmarshalled_metadata.errors
        assert 'authors' in deserialized_metadata
        assert deserialized_metadata['authors'][0] == {
            'first_name': 'John',
            'middle_name': 'Jacob',
            'last_name': 'Smith',
            'full_name': 'Smith, John Jacob'
        }
        assert deserialized_metadata['authors'][1] == {
            'first_name': 'Jane',
            'middle_name': 'Janet',
            'last_name': 'Doe',
            'full_name': 'Doe, Jane Janet'
        }

    def test_resource_type_loaded(self, create_input_metadatav1):
        serialized_record = create_input_metadatav1({
            'resource_type': {
                'general': 'other',
                'specific': 'other'
            }
        })

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record)
        deserialized_metadata = unmarshalled_metadata.data

        assert not unmarshalled_metadata.errors
        assert 'resource_type' in deserialized_metadata

    def test_empty_required_key_returns_errors(self, create_input_metadatav1):
        serialized_record = create_input_metadatav1({'title': None})

        unmarshalled_record = MetadataSchemaV1().load(serialized_record)

        assert 'title' in unmarshalled_record.errors

    def test_description_too_short_returns_error(
            self, create_input_metadatav1):
        serialized_record = create_input_metadatav1({'description': 'A '})

        unmarshalled_record = MetadataSchemaV1().load(serialized_record)

        assert 'description' in unmarshalled_record.errors

    # WHY: We place these tests here because we plan on having terms be a
    #      first-class citizen of the records schema
    def test_one_term_loaded(self, create_input_metadatav1):
        terms = [
            {
                'source': 'MeSH',
                'value': 'Cognitive Neuroscience',
                'id': 'D000066494'
            }
        ]
        serialized_record = create_input_metadatav1({
            'terms': [{'data': term} for term in terms]
        })

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record)
        deserialized_metadata = unmarshalled_metadata.data

        assert not unmarshalled_metadata.errors
        assert 'terms' in deserialized_metadata
        assert deserialized_metadata['terms'] == terms

    def test_multiple_terms_loaded(self, create_input_metadatav1):
        terms = [
            {
                'source': 'MeSH',
                'value': 'Cognitive Neuroscience',
                'id': 'D000066494'
            },
            {
                'source': 'MeSH',
                'value': 'Acanthamoeba',
                'id': 'D000048'
            }
        ]
        serialized_record = create_input_metadatav1({
            'terms': [{'data': term} for term in terms]
        })

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record)
        deserialized_metadata = unmarshalled_metadata.data

        assert not unmarshalled_metadata.errors
        assert 'terms' in deserialized_metadata
        assert deserialized_metadata['terms'] == terms

    def test_no_terms_loaded(self, create_input_metadatav1):
        terms = []
        serialized_record = create_input_metadatav1({
            'terms': terms
        })

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record)
        deserialized_metadata = unmarshalled_metadata.data

        assert not unmarshalled_metadata.errors
        assert 'terms' in deserialized_metadata
        assert deserialized_metadata['terms'] == terms

        serialized_record2 = create_input_metadatav1()

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record2)
        deserialized_metadata = unmarshalled_metadata.data

        assert not unmarshalled_metadata.errors
        assert 'terms' in deserialized_metadata
        assert deserialized_metadata['terms'] == terms

        serialized_record3 = create_input_metadatav1({
            'terms': [None, {}, {'data': None}, {'data': {}}, '']
        })

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record3)
        deserialized_metadata = unmarshalled_metadata.data

        assert not unmarshalled_metadata.errors
        assert 'terms' in deserialized_metadata
        assert deserialized_metadata['terms'] == []

    def test_incorrect_format_terms_returns_error(
            self, create_input_metadatav1):
        terms = ["bar"]
        serialized_record = create_input_metadatav1({
            'terms': terms
        })

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record)
        deserialized_metadata = unmarshalled_metadata.data

        assert 'terms' in unmarshalled_metadata.errors
        assert deserialized_metadata['terms'] == [{}]

    def test_coalesce_terms_loaded(self, create_input_metadatav1):
        terms = [
            {
                'source': 'MeSH',
                'value': 'Cognitive Neuroscience',
                'id': 'D000066494'
            },
            {
                'source': 'FAST',
                'value': 'Glucagonoma',
                'id': '943672'
            }
        ]

        serialized_record = create_input_metadatav1({
            'mesh_terms': [{'data': terms[0]}],
            'fast_terms': [{'data': terms[1]}]
        })

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record)
        deserialized_metadata = unmarshalled_metadata.data

        assert not unmarshalled_metadata.errors
        assert 'terms' in deserialized_metadata
        assert 'mesh_terms' not in deserialized_metadata
        assert 'fast_terms' not in deserialized_metadata
        assert deserialized_metadata['terms'] == terms

    def test_permissions_loaded(self, create_input_metadatav1):
        serialized_record = create_input_metadatav1({
            'permissions': 'restricted_view'
        })

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record)
        deserialized_metadata = unmarshalled_metadata.data

        assert not unmarshalled_metadata.errors
        assert deserialized_metadata['permissions'] == 'restricted_view'

    def test_invalid_permissions_returns_errors(
            self, create_input_metadatav1):
        serialized_record = create_input_metadatav1({
            'permissions': 'foo_view'
        })

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record)
        deserialized_metadata = unmarshalled_metadata.data

        assert 'permissions' in unmarshalled_metadata.errors


class TestAuthorSchemaV1(object):
    def test_first_and_last_name_required(self):
        author = {
            'first_name': 'Jonathan',
        }

        unmarshalled_author = AuthorSchemaV1().load(author)

        assert 'first_name' in unmarshalled_author.data
        assert 'middle_name' not in unmarshalled_author.errors
        assert 'last_name' in unmarshalled_author.errors


class TestResourceTypeSchemaV1(object):
    def test_general_dataset_fills_specific_dataset(self):
        resource_type = {
            'general': 'dataset'
        }

        unmarshalled_resource_type = ResourceTypeSchemaV1().load(resource_type)

        assert not unmarshalled_resource_type.errors
        assert 'general' in unmarshalled_resource_type.data
        assert unmarshalled_resource_type.data['specific'] == 'dataset'

    def test_valid_general_specific_combination_loads(self):
        resource_type = {
            'general': 'text resources',
            'specific': 'letter'
        }

        unmarshalled_resource_type = ResourceTypeSchemaV1().load(resource_type)
        loaded_resource_type = unmarshalled_resource_type.data

        assert not unmarshalled_resource_type.errors
        assert loaded_resource_type['general'] == 'text resources'
        assert loaded_resource_type['specific'] == 'letter'

    def test_invalid_general_specific_combination_errors(self):
        resource_type = {
            'general': 'articles',
            'specific': 'other'
        }

        unmarshalled_resource_type = ResourceTypeSchemaV1().load(resource_type)

        assert (
            unmarshalled_resource_type.errors['_schema'][0] ==
            'Invalid resource type.'
        )

    def test_general_specific_combination_maps_to_hierarchy(self):
        resource_type = {
            'general': 'text resources',
            'specific': 'letter'
        }

        unmarshalled_resource_type = ResourceTypeSchemaV1().load(resource_type)
        loaded_resource_type = unmarshalled_resource_type.data
        assert loaded_resource_type['full_hierarchy'] == ['text', 'letter']
