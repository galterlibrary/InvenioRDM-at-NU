from cd2h_repo_project.modules.records.marshmallow.json import (
    MetadataSchemaV1, RecordSchemaV1
)


class TestRecordSchemaV1(object):
    def test_load_for_empty_json_contains_schema(self):
        unmarshalled_record = RecordSchemaV1().load({})

        assert not unmarshalled_record.errors
        assert unmarshalled_record.data == {
            '$schema': ('https://cd2hrepo.galter.northwestern.edu/'
                        'schemas/records/record-v0.1.0.json'),
        }

    def test_load_for_valid_json_removes_metadata_envelope(
            self, create_serialized_record):
        enveloped_record = {
            'metadata': create_serialized_record()
        }

        unmarshalled_record = RecordSchemaV1().load(enveloped_record)

        assert not unmarshalled_record.errors
        loaded_record = unmarshalled_record.data
        assert 'metadata' not in loaded_record
        assert loaded_record['title'] == 'A title'
        assert loaded_record['description'] == 'A description'
        assert loaded_record['author'] == 'An author'
        assert loaded_record['license'] == 'mit-license'

    def test_load_for_invalid_json_returns_errors(self):
        serialized_record = {'foo': 'bar'}

        unmarshalled_record = RecordSchemaV1().load(serialized_record)

        assert 'foo' in unmarshalled_record.errors
        assert not unmarshalled_record.data


class TestMetadataSchemaV1(object):

    def test_extra_key_is_ignored(self, create_serialized_record):
        serialized_record = create_serialized_record({'foo': 'bar'})

        unmarshalled_record = MetadataSchemaV1().load(serialized_record)
        loaded_record = unmarshalled_record.data

        # marshmallow does not care about additional keys
        assert 'foo' not in unmarshalled_record.errors
        assert 'foo' not in loaded_record

    def test_missing_keys_return_errors(self):
        serialized_record = {'foo': 'bar'}

        unmarshalled_record = MetadataSchemaV1().load(serialized_record)

        required_keys = [
            'title', 'description', 'author', 'license', 'permissions'
        ]
        assert set(unmarshalled_record.errors.keys()) == set(required_keys)
        assert (
            unmarshalled_record.errors['title'] ==
            ['Missing data for required field.']
        )

    def test_empty_required_key_returns_errors(self, create_serialized_record):
        serialized_record = create_serialized_record({'title': None})

        unmarshalled_record = MetadataSchemaV1().load(serialized_record)

        assert 'title' in unmarshalled_record.errors
        # Partial validation is allowed
        loaded_record = unmarshalled_record.data
        assert loaded_record['description'] == 'A description'
        assert loaded_record['author'] == 'An author'

    def test_description_too_short_returns_error(
            self, create_serialized_record):
        serialized_record = create_serialized_record({'description': 'A '})

        unmarshalled_record = MetadataSchemaV1().load(serialized_record)

        assert 'description' in unmarshalled_record.errors

    def test_one_term_loaded(self, create_serialized_record):
        terms = [{'source': 'MeSH', 'value': 'Cognitive Neuroscience'}]
        serialized_record = create_serialized_record({
            'terms': terms
        })

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record)
        deserialized_metadata = unmarshalled_metadata.data

        assert not unmarshalled_metadata.errors
        assert 'terms' in deserialized_metadata
        assert deserialized_metadata['terms'] == terms

    def test_multiple_terms_loaded(self, create_serialized_record):
        terms = [
            {'source': 'MeSH', 'value': 'Cognitive Neuroscience'},
            {'source': 'MeSH', 'value': 'Acanthamoeba'}
        ]
        serialized_record = create_serialized_record({
            'terms': terms
        })

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record)
        deserialized_metadata = unmarshalled_metadata.data

        assert not unmarshalled_metadata.errors
        assert 'terms' in deserialized_metadata
        assert deserialized_metadata['terms'] == terms

    def test_no_terms_loaded(self, create_serialized_record):
        terms = []
        serialized_record = create_serialized_record({
            'terms': terms
        })

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record)
        deserialized_metadata = unmarshalled_metadata.data

        assert not unmarshalled_metadata.errors
        assert 'terms' in deserialized_metadata
        assert deserialized_metadata['terms'] == terms

        serialized_record2 = create_serialized_record()

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record2)
        deserialized_metadata = unmarshalled_metadata.data

        assert not unmarshalled_metadata.errors
        assert 'terms' in deserialized_metadata
        assert deserialized_metadata['terms'] == terms

    def test_incorrect_format_terms_returns_error(
            self, create_serialized_record):
        terms = ["bar"]
        serialized_record = create_serialized_record({
            'terms': terms
        })

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record)
        deserialized_metadata = unmarshalled_metadata.data

        assert 'terms' in unmarshalled_metadata.errors
        assert deserialized_metadata['terms'] == [{}]

    def test_coalesce_terms_loaded(self, create_serialized_record):
        terms = [
            {'source': 'MeSH', 'value': 'Cognitive Neuroscience'},
            {'source': 'FAST', 'value': 'Glucagonoma'}
        ]

        serialized_record = create_serialized_record({
            'mesh_terms': [terms[0]],
            'fast_terms': [terms[1]],
        })

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record)
        deserialized_metadata = unmarshalled_metadata.data

        assert not unmarshalled_metadata.errors
        assert 'terms' in deserialized_metadata
        assert 'mesh_terms' not in deserialized_metadata
        assert 'fast_terms' not in deserialized_metadata
        assert deserialized_metadata['terms'] == terms

    def test_permissions_loaded(self, create_serialized_record):
        serialized_record = create_serialized_record({
            'permissions': 'restricted_view'
        })

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record)
        deserialized_metadata = unmarshalled_metadata.data

        assert not unmarshalled_metadata.errors
        assert deserialized_metadata['permissions'] == 'restricted_view'

    def test_invalid_permissions_returns_errors(
            self, create_serialized_record):
        serialized_record = create_serialized_record({
            'permissions': 'foo_view'
        })

        unmarshalled_metadata = MetadataSchemaV1().load(serialized_record)
        deserialized_metadata = unmarshalled_metadata.data

        assert 'permissions' in unmarshalled_metadata.errors
