"""Test Search integration."""

import json
from io import BytesIO

from invenio_records_rest.facets import _post_filter
from invenio_records_rest.sorter import default_sorter_factory
from invenio_search import current_search
from werkzeug.datastructures import MultiDict

from cd2h_repo_project.modules.records.api import RecordType
from cd2h_repo_project.modules.records.permissions import RecordPermissions
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
    for key in ['title', 'authors', 'description', 'resource_type', 'type']:
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

    def test_search_by_partial_author_returns_record(
            self, client, create_record, es_clear):
        record1 = create_record(
            {
                'authors': [
                    {
                        'first_name': 'John',
                        'last_name': 'Smith',
                        'full_name': 'Smith, John'
                    }
                ]
            }
        )
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

    def test_search_nested_post_filter_filters_records(
            self, client, create_record, es_clear):
        record1 = create_record(
            {
                'terms': [
                    {'source': 'MeSH', 'value': 'Diabetes Complications'},
                ]
            }
        )
        record2 = create_record(
            {
                'terms': [
                    {'source': 'FAST', 'value': 'Diabetes--Complications'},
                ]
            }
        )

        response = client.get("/records/?subjects=MeSH")

        assert_single_hit(response, record1)

        response = client.get("/records/?subject=Diabetes--Complications")

        assert_single_hit(response, record2)

    def test_search_is_selective_about_sort_field(self, app, config):
        sort_fields = [
            v['fields'] for (k, v) in
            config['RECORDS_REST_SORT_OPTIONS']['records'].items()
        ]
        assert ['-_score'] in sort_fields
        assert ['_score'] in sort_fields
        assert ['_created'] in sort_fields
        assert ['-_created'] in sort_fields
        assert ['_updated'] in sort_fields
        assert ['-_updated'] in sort_fields
        assert ['title.raw'] in sort_fields
        assert ['-title.raw'] in sort_fields

        with app.test_request_context('?sort=title_asc'):
            search = RecordsSearch().query()
            search, args = default_sorter_factory(search, "records")

            search_dict = search.to_dict()
            assert 'sort' in search_dict

        with app.test_request_context('?sort=invalid'):
            search = RecordsSearch().query()
            search, args = default_sorter_factory(search, "records")

            search_dict = search.to_dict()
            assert 'sort' not in search_dict

    def test_search_sort_orders_records(
            self, client, create_record, es_clear):
        record2 = create_record({"title": "ZZZyxas' True Abyss"})
        record1 = create_record({"title": "Aardvark true facts"})

        # Case for 'title_asc' (special because it is a 'text' type)
        response = client.get("/records/?sort=title_asc")

        hit1 = response.json['hits']['hits'][0]
        assert hit1['metadata']['title'] == "Aardvark true facts"

        # Case for 'updated_desc'
        response = client.get("/records/?sort=updated_desc")

        hit1 = response.json['hits']['hits'][0]
        assert hit1['metadata']['title'] == "Aardvark true facts"

        # Case for 'bestmatch_asc'
        response = client.get("/records/?q=true+facts&sort=bestmatch_asc")

        hit1 = response.json['hits']['hits'][0]
        assert hit1['metadata']['title'] == "ZZZyxas' True Abyss"

    def test_search_orders_by_created_desc_if_no_query(
            self, client, create_record, es_clear):
        record1 = create_record({"title": "old record"})
        record2 = create_record({"title": "More recent record"})

        response = client.get("/records/")

        hit1 = response.json['hits']['hits'][0]
        assert hit1['metadata']['title'] == "More recent record"
        hit2 = response.json['hits']['hits'][1]
        assert hit2['metadata']['title'] == "old record"

    def test_search_orders_by_bestmatch_desc_if_query_but_no_sort(
            self, client, create_record, es_clear):
        record1 = create_record({"title": "old record"})
        record2 = create_record({"title": "More recent record"})

        response = client.get("/records/?q=old+record")

        hit1 = response.json['hits']['hits'][0]
        assert hit1['metadata']['title'] == "old record"
        hit2 = response.json['hits']['hits'][1]
        assert hit2['metadata']['title'] == "More recent record"

    def test_search_returns_restricted_access_results_to_authenticated_user(
            self, client, create_record, create_user, es_clear):
        record = create_record(
            {
                "title": "old record",
                "permissions": RecordPermissions.RESTRICTED_VIEW
            }
        )

        response = client.get("/records/?q=old+record")

        assert response.status_code == 200
        assert len(response.json['hits']['hits']) == 0

        # WARNING: If user is logged in before create_record,
        #          then create_record assigns that user as the owner
        user = create_user()
        login_request_and_session(user, client)

        response = client.get("/records/?q=old+record")

        assert_single_hit(response, record)

    def test_search_returns_private_access_results_to_owner(
            self, client, create_record, create_user, es_clear):

        # TODO: Improve User factory to auto-generate unique emails
        user1 = create_user({'email': 'user1@example.com'})
        user2 = create_user({'email': 'user2@example.com'})
        record = create_record(
            {
                "title": "old record",
                "permissions": RecordPermissions.PRIVATE_VIEW,
                "_deposit": {"owners": [user1.id]}
            }
        )

        # WARNING: If user is logged in before create_record,
        #          then create_record assigns that user as the owner
        login_request_and_session(user2, client)

        response = client.get("/records/?q=old+record")

        assert response.status_code == 200
        assert len(response.json['hits']['hits']) == 0

        login_request_and_session(user1, client)

        response = client.get("/records/?q=old+record")

        assert_single_hit(response, record)

    def test_search_by_general_resource_type_returns_record(
            self, client, create_record, es_clear):
        record1 = create_record(
            {
                'resource_type': {
                    'general': 'articles',
                    'specific': 'journal article',
                    'full_hierarchy': [
                        'text',
                        'periodical',
                        'journal',
                        'contribution to journal'
                    ]
                }
            }
        )
        record2 = create_record()

        response = client.get("/records/?q=articles")

        assert_single_hit(response, record1)

    def test_search_by_specific_resource_type_returns_record(
            self, client, create_record, es_clear):
        record1 = create_record(
            {
                'resource_type': {
                    'general': 'articles',
                    'specific': 'journal article',
                    'full_hierarchy': [
                        'text',
                        'periodical',
                        'journal',
                        'contribution to journal'
                    ]
                }
            }
        )
        record2 = create_record()

        response = client.get("/records/?q=journal+article")

        assert_single_hit(response, record1)

    def test_search_by_hierarchy_resource_type_returns_record(
            self, client, create_record, es_clear):
        record1 = create_record(
            {
                'resource_type': {
                    'general': 'articles',
                    'specific': 'journal article',
                    'full_hierarchy': [
                        'text',
                        'periodical',
                        'journal',
                        'contribution to journal'
                    ]
                }
            }
        )
        record2 = create_record()

        response = client.get("/records/?q=periodical")

        assert_single_hit(response, record1)

    def test_search_aggregates_by_resource_type(
            self, client, create_record, es_clear):
        record1 = create_record(
            {
                'resource_type': {
                    'general': 'learning objects',
                    'specific': 'examination questions',
                    'full_hierarchy': [
                        'learning object', 'examination questions'
                    ]
                }
            }
        )
        record2 = create_record(
            {
                'resource_type': {
                    'general': 'dataset',
                    'specific': 'dataset',
                    'full_hierarchy': ['dataset', 'dataset']
                }
            }
        )

        response = client.get("/records/?resource_type=learning+objects")

        aggregations = response.json['aggregations']
        assert len(aggregations['resource_type']['buckets'])

        def dataset_cond(bucket):
            return (
                bucket['key'] == 'dataset' and
                bucket['rt_specific']['buckets'][0]['key'] == 'dataset'
            )

        assert any(
            dataset_cond(b) for b in aggregations['resource_type']['buckets']
        )

        def learning_objects_cond(bucket):
            return (
                bucket['key'] == 'learning objects' and
                bucket['rt_specific']['buckets'][0]['key'] ==
                'examination questions'
            )

        assert any(
            learning_objects_cond(b)
            for b in aggregations['resource_type']['buckets']
        )
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
