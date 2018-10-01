from datetime import datetime

from cd2h_repo_project.modules.records.marshmallow.json import (
    MetadataSchemaV1, RecordSchemaV1
)
from cd2h_repo_project.modules.records.serializers import json_v1


def test_json_v1_serializes_persistent_identifier(create_record):
    record = create_record()

    serialized_record = json_v1.transform_record(record.pid, record)

    assert serialized_record['id'] == record.pid.pid_value


def test_json_v1_serializes_dump_onlys(create_record):
    record = create_record()

    serialized_record = json_v1.transform_record(record.pid, record)

    assert 'created' in serialized_record
    assert 'updated' in serialized_record
    assert 'links' in serialized_record


def test_json_v1_serializes_metadata(create_record):
    record = create_record()

    serialized_record = json_v1.transform_record(record.pid, record)

    assert serialized_record['metadata']['title']
    assert serialized_record['metadata']['description']
    assert serialized_record['metadata']['author']
