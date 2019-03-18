"""Test Search integration."""

import json
from io import BytesIO

from invenio_records_rest.facets import _post_filter
from invenio_search import current_search
from werkzeug.datastructures import MultiDict

from cd2h_repo_project.modules.records.api import RecordType
from cd2h_repo_project.modules.records.search import RecordsSearch
from utils import login_request_and_session


def assert_single_hit(response, expected_record):
    assert response.status_code == 200

    search_hits = response.json['hits']['hits']

    # Kept for debugging
    for hit in search_hits:
        print("Search hit:", json.dumps(hit, indent=4, sort_keys=True))

    assert len(search_hits) == 1
    search_hit = search_hits[0]
    # only a record that has been published has an id, so we don't check for it
    for key in ['created', 'updated', 'metadata', 'links']:
        assert key in search_hit
    for key in ['title', 'author', 'description', 'type']:
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

    def test_search_is_selective_about_post_filter(self, app, config):
        post_filters = config['RECORDS_REST_FACETS']['records']['post_filters']
        assert 'file_type' in post_filters

        with app.test_request_context('?file_type=png'):
            search = RecordsSearch().query()

            search, args = _post_filter(search, MultiDict(), post_filters)

            search_dict = search.to_dict()
            assert 'post_filter' in search_dict

        with app.test_request_context('?not_a_post_filter=png'):
            search = RecordsSearch().query()

            search, args = _post_filter(search, MultiDict(), post_filters)

            search_dict = search.to_dict()
            assert 'post_filter' not in search_dict

    def test_search_post_filter_filters_records(
            self, client, create_record, es_clear):
        deposit = create_record(published=False)
        deposit.files['test.txt'] = BytesIO(b'Hello world!')
        deposit.publish()
        _, record1 = deposit.fetch_published()
        record2 = create_record()

        response = client.get("/records/?file_type=txt")

        assert_single_hit(response, record1)

    def test_search_post_filter_aggregates_records(
            self, client, create_record, es_clear):
        deposit = create_record(published=False)
        deposit.files['test.txt'] = BytesIO(b'Hello world!')
        deposit.publish()
        _, record1 = deposit.fetch_published()
        record2 = create_record()

        response = client.get("/records/?file_type=txt")

        assert 'file_type' in response.json['aggregations']


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

    def test_search_only_returns_appropriate_records(
            self, client, create_record, es_clear, create_user, db):
        user = create_user()
        login_request_and_session(user, client)

        print("Case: Newly created (draft) record should be returned")
        unpublished_record = create_record(
            {'title': 'A New Record'}, published=False)

        response = client.get('/deposits/')

        assert_single_hit(response, unpublished_record)
        print("****")

        print("Case: When published, only published record should be returned")
        unpublished_record.publish()
        db.session.commit()
        current_search.flush_and_refresh(index='*')
        pid, published_record = unpublished_record.fetch_published()

        response = client.get('/deposits/')

        assert_single_hit(response, published_record)
        print("****")

        print("Case: When edited, draft and published record should be "
              "returned")
        edited_record = unpublished_record.edit()
        current_search.flush_and_refresh(index='*')
        db.session.commit()

        response = client.get('/deposits/')
        search_hits = response.json['hits']['hits']

        assert response.status_code == 200
        assert len(search_hits) == 2
        hit_types = [hit['metadata']['type'] for hit in search_hits]
        assert published_record['type'] == RecordType.published.value
        assert published_record['type'] in hit_types
        assert edited_record['type'] == RecordType.draft.value
        assert edited_record['type'] in hit_types
        print("****")

        # Case: When edited record is published,
        print("Case: When re-published, only published record should be "
              "returned")
        edited_record.publish()
        db.session.commit()
        current_search.flush_and_refresh(index='*')
        pid, published_record = edited_record.fetch_published()

        response = client.get('/deposits/')

        assert_single_hit(response, published_record)
        print("****")
