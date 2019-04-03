from datetime import date

import pytest
from flask import current_app
from invenio_pidstore.models import PersistentIdentifier

from cd2h_repo_project.modules.doi.serializers import datacite_v41
from cd2h_repo_project.modules.records.minters import mint_pids_for_record
from cd2h_repo_project.modules.records.serializers import json_v1


class TestJsonV1(object):
    def test_serializes_persistent_identifier(self, create_record):
        record = create_record()
        pid = PersistentIdentifier.get(
            record['_deposit']['pid']['type'],
            record['_deposit']['pid']['value'],
        )

        serialized_record = json_v1.transform_record(pid, record)

        assert serialized_record['id'] == record['_deposit']['pid']['value']

    def test_serializes_dump_onlys(self, create_record):
        record = create_record()
        pid = PersistentIdentifier.get(
            record['_deposit']['pid']['type'],
            record['_deposit']['pid']['value'],
        )

        serialized_record = json_v1.transform_record(pid, record)

        assert 'created' in serialized_record
        assert 'updated' in serialized_record
        assert 'links' in serialized_record

    def test_serializes_metadata(self, create_record):
        record = create_record()
        pid = PersistentIdentifier.get(
            record['_deposit']['pid']['type'],
            record['_deposit']['pid']['value'],
        )

        serialized_record = json_v1.transform_record(pid, record)

        required_keys = ['title', 'description', 'author', 'license']
        for key in required_keys:
            assert serialized_record['metadata'][key]


@pytest.fixture
def serialized_record(create_record):
    record = create_record(published=False)
    mint_pids_for_record(record.id, record)
    pid = PersistentIdentifier.get('doi', record['id'])
    return datacite_v41.serialize(pid, record)


class TestDataCiteV4(object):
    """Test DataCiteV4 serialization"""

    def test_serializes_empty_identifier(self, serialized_record):
        # Expect empty identifier so that DataCite generates it
        assert (
            '<identifier identifierType="DOI"></identifier>' in
            serialized_record
        )

    def test_serializes_creators(self, serialized_record):
        # TODO: Test for multiple authors when we provide multiple author
        #       input fields
        assert "<creators>\n" in serialized_record
        assert "<creator>\n" in serialized_record
        assert "<creatorName>author, An</creatorName>\n" in serialized_record
        assert "</creator>\n" in serialized_record
        assert "</creators>" in serialized_record

    def test_serializes_titles(self, serialized_record):
        assert "<titles>\n" in serialized_record
        assert "<title>A title</title>" in serialized_record
        assert "</titles>\n" in serialized_record

    def test_serializes_publisher(self, serialized_record):
        assert (
            "<publisher>{}</publisher>".format(
                current_app.config['DOI_PUBLISHER']) in serialized_record
        )

    def test_serializes_publicationYear(self, serialized_record):
        assert (
            "<publicationYear>{}</publicationYear>".format(date.today().year)
            in serialized_record
        )

    def test_serializes_resourceType(self, serialized_record):
        # TODO: Adjust if when we provide resource type as an input field
        assert (
            '<resourceType resourceTypeGeneral="Dataset">Dataset'
            '</resourceType>' in serialized_record
        )
