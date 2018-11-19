"""Test Search integration."""

import uuid

import pytest
from flask import current_app, url_for
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record
from invenio_search import current_search

from utils import login_request_and_session


def assert_single_hit(response, expected_record):
    assert response.status_code == 200
    assert len(response.json['hits']['hits']) == 1
    search_hit = response.json['hits']['hits'][0]
    for key in ['id', 'created', 'updated', 'metadata', 'links']:
        assert key in search_hit
    for key in ['title', 'author', 'description']:
        assert search_hit['metadata'][key] == expected_record[key]


class TestRecordsSearch(object):

    def test_search_returns_published_records(
            self, client, create_record, es_clear):
        unpublished_record = create_record(
            {'title': 'Unpublished'}, published=False
        )
        published_record = create_record()

        response = client.get("/records/")

        assert_single_hit(response, published_record)

    def test_search_for_query_part_of_title_returns_record(
            self, client, create_record, es_clear):
        record1 = create_record({'title': 'Test Aardvark'})
        record2 = create_record()

        response = client.get("/records/?q=Aardvark")

        assert_single_hit(response, record1)

    def test_search_for_part_of_query_part_of_title_returns_record(
            self, client, create_record, es_clear):
        record1 = create_record({'title': 'Test Aardvark'})
        record2 = create_record()

        response = client.get("/records/?q=Animal+Aardvark")

        assert_single_hit(response, record1)

    def test_search_for_query_not_part_of_title_doesnt_return_record(
            self, client, create_record, es_clear):
        record1 = create_record({'title': 'Test Aardvark'})
        record2 = create_record()

        response = client.get("/records/?q=Pangolin")

        assert response.status_code == 200
        assert len(response.json['hits']['hits']) == 0

    def test_search_casing_does_not_matter(
            self, client, create_record, es_clear):
        record1 = create_record({'title': 'Test Aardvark'})
        record2 = create_record()

        response = client.get("/records/?q=aardvark")

        assert_single_hit(response, record1)

    def test_search_does_not_contain_owner_draft_records(
            self, client, create_record, es_clear, create_user):
        user = create_user()
        login_request_and_session(user, client)
        unpublished_record = create_record(
            {'title': 'Unpublished'}, published=False
        )
        published_record = create_record()

        response = client.get("/records/")

        assert_single_hit(response, published_record)

    def test_search_for_query_part_of_author_returns_record(
            self, client, create_record, es_clear):
        # NOTE: This test is enough to validate that the author field uses
        #       text indexing
        record1 = create_record({'author': 'John Smith'})
        record2 = create_record()

        response = client.get("/records/?q=john")

        assert_single_hit(response, record1)

    def test_search_for_query_part_of_description_returns_record(
            self, client, create_record, es_clear):
        record1 = create_record({'description': 'In a galaxy far far away...'})
        record2 = create_record()

        response = client.get("/records/?q=far+galaxy")

        assert_single_hit(response, record1)


class TestDepositsSearch(object):

    def test_search_contains_owner_published_and_draft_records(
            self, client, create_record, es_clear, create_user):
        # Another user to scramble things
        another_user = create_user({'email': 'another@example.com'})
        login_request_and_session(another_user, client)
        another_published_record = create_record(
            {'title': 'Another Published Record'})
        # The user we want to test
        user = create_user()
        login_request_and_session(user, client)
        published_record = create_record({'title': 'A Published Record'})
        unpublished_record = create_record(
            {'title': 'A Draft Record'}, published=False)

        response = client.get('/deposits/')
        search_hits = response.json['hits']['hits']

        assert response.status_code == 200
        assert len(search_hits) == 2
        hit_titles = [hit['metadata']['title'] for hit in search_hits]
        assert published_record['title'] in hit_titles
        assert unpublished_record['title'] in hit_titles
        assert another_published_record['title'] not in hit_titles
