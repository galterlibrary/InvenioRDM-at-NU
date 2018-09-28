"""Test Search integration."""

import uuid

import pytest
from flask import current_app, url_for
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record
from invenio_search import current_search


# TODO: Improve test performance by indexing/clearing only once
@pytest.fixture
def create_indexed_record(create_record, es_clear):
    """Return indexed records."""

    def _create_indexed_record(*args, **kwargs):
        record = create_record(*args, **kwargs)
        RecordIndexer().index(record)
        search_class = (
            current_app.config.get('RECORDS_REST_ENDPOINTS', {})
            .get('recid', {})
            .get('search_class')
        )
        current_search.flush_and_refresh(index=search_class.Meta.index)
        return record

    return _create_indexed_record


def assert_single_hit(response, expected_record):
    assert response.status_code == 200
    assert len(response.json['hits']['hits']) == 1
    search_hit = response.json['hits']['hits'][0]
    for key in ['id', 'created', 'updated', 'metadata', 'links']:
        assert key in search_hit
    for key in ['title', 'author', 'description']:
        assert search_hit['metadata'][key] == expected_record[key]


def test_search_returns_published_records(
        client, create_indexed_record):
    unpublished_record = create_indexed_record(
        {'title': 'Unpublished'}, published=False
    )
    published_record = create_indexed_record()

    response = client.get(
        url_for('invenio_records_rest.recid_list')
    )

    assert_single_hit(response, published_record)


def test_search_for_query_part_of_title_returns_record(
        client, create_indexed_record):
    record1 = create_indexed_record({'title': 'Test Aardvark'})
    record2 = create_indexed_record()

    response = client.get(
        url_for('invenio_records_rest.recid_list'),
        query_string={'q': 'Aardvark'}
    )

    assert_single_hit(response, record1)


def test_search_for_part_of_query_part_of_title_returns_record(
        client, create_indexed_record):
    record1 = create_indexed_record({'title': 'Test Aardvark'})
    record2 = create_indexed_record()

    response = client.get(
        url_for('invenio_records_rest.recid_list'),
        query_string={'q': 'Animal Aardvark'}
    )

    assert_single_hit(response, record1)


def test_search_for_query_not_part_of_title_doesnt_return_record(
        client, create_indexed_record):
    record1 = create_indexed_record({'title': 'Test Aardvark'})
    record2 = create_indexed_record()

    response = client.get(
        url_for('invenio_records_rest.recid_list'),
        query_string={'q': 'Pangolin'}
    )

    assert response.status_code == 200
    assert len(response.json['hits']['hits']) == 0


def test_search_casing_does_not_matter(client, create_indexed_record):
    record1 = create_indexed_record({'title': 'Test Aardvark'})
    record2 = create_indexed_record()

    response = client.get(
        url_for('invenio_records_rest.recid_list'),
        query_string={'q': 'aardvark'}
    )

    assert_single_hit(response, record1)
