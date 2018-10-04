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


class Test_MetadataSchemaV1Unique(object):

    def test_extra_key_doesnt_return_errors(self, create_serialized_record):
        serialized_record = create_serialized_record({'foo': 'bar'})

        unmarshalled_record = MetadataSchemaV1().load(serialized_record)

        # marshmallow does not care about additional keys
        assert 'foo' not in unmarshalled_record.errors

    def test_missing_keys_return_errors(self):
        serialized_record = {'foo': 'bar'}

        unmarshalled_record = MetadataSchemaV1().load(serialized_record)

        missing_keys = ['title', 'description', 'author', 'license']
        assert set(unmarshalled_record.errors) == set(missing_keys)
        assert not unmarshalled_record.data

    def test_empty_required_key_return_errors(self, create_serialized_record):
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
