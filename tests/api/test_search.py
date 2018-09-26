"""Test Search integration."""

import uuid

import pytest
from flask import current_app, url_for
from invenio_indexer.api import RecordIndexer
from invenio_pidstore import current_pidstore
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record
from invenio_search import RecordsSearch, current_search


def create_record(data):
    record_uuid = uuid.uuid4()
    # creates PID AND sets data['id'] to it (invenio way)
    current_pidstore.minters['recid'](record_uuid, data)
    return Record.create(data)


@pytest.fixture
def search_records(db):
    record1 = create_record({
        '$schema': (
            current_app.extensions['invenio-jsonschemas']
            .path_to_url('records/record-v0.1.0.json')
        ),
        'title': 'Test Aardvark',
        'author': 'An author',
        'description': 'A description',
        '_deposit': {}
    })

    record2 = create_record({
        '$schema': (
            current_app.extensions['invenio-jsonschemas']
            .path_to_url('records/record-v0.1.0.json')
        ),
        'title': 'Test Content',
        'author': 'An author',
        'description': 'A description',
        '_deposit': {}
    })

    db.session.commit()

    return record1, record2


# TODO: Improve test performance by indexing only once
@pytest.fixture
def indexed_records(search_records, es_clear):
    """Return indexed records."""
    indexer = RecordIndexer()
    search_class = (
        current_app.config.get('RECORDS_REST_ENDPOINTS', {})
        .get('recid', {})
        .get('search_class')
    )

    for record in search_records:
        indexer.index(record)

    current_search.flush_and_refresh(index=search_class.Meta.index)

    return search_records


def test_search_for_query_part_of_title_returns_record(
        client, indexed_records):
    response = client.get(
        url_for('invenio_records_rest.recid_list'),
        query_string={'q': 'Aardvark'}
    )

    assert response.status_code == 200
    assert len(response.json['hits']['hits']) == 1
    search_hit = response.json['hits']['hits'][0]
    for key in ['id', 'created', 'updated', 'metadata', 'links']:
        assert key in search_hit
    expected_record = indexed_records[0]
    for key in ['title', 'author', 'description']:
        assert search_hit['metadata'][key] == expected_record[key]


def test_search_for_part_of_query_part_of_title_returns_record(
        client, indexed_records):
    response = client.get(
        url_for('invenio_records_rest.recid_list'),
        query_string={'q': 'Test Aardvark'}
    )

    assert response.status_code == 200
    assert len(response.json['hits']['hits']) == 2


def test_search_for_query_not_part_of_title_doesnt_return_record(
        client, indexed_records):
    response = client.get(
        url_for('invenio_records_rest.recid_list'),
        query_string={'q': 'Pangolin'}
    )

    assert response.status_code == 200
    assert len(response.json['hits']['hits']) == 0


def test_search_casing_does_not_matter(client, indexed_records):
    response = client.get(
        url_for('invenio_records_rest.recid_list'),
        query_string={'q': 'aardvark'}
    )

    assert response.status_code == 200
    assert len(response.json['hits']['hits']) == 1
    search_hit = response.json['hits']['hits'][0]
    for key in ['id', 'created', 'updated', 'metadata', 'links']:
        assert key in search_hit
    expected_record = indexed_records[0]
    for key in ['title', 'author', 'description']:
        assert search_hit['metadata'][key] == expected_record[key]
