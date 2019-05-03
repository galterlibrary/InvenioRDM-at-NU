"""Test MeSH extractor."""

from os.path import dirname, join, realpath

import pytest
from elasticsearch.helpers import bulk

from cd2h_repo_project.modules.terms.loaders import mesh_indexable
from cd2h_repo_project.modules.terms.mesh import MeSH
from cd2h_repo_project.modules.terms.suggester import suggest_terms


@pytest.fixture(scope='module')
def index_mesh_terms(es):
    filename = 'descriptors_test_file.txt'
    filepath = join(dirname(realpath(__file__)), filename)
    terms = MeSH.load(filepath, filter='topics')

    index_name = 'terms-term-v1.0.0'
    type_name = 'term-v1.0.0'
    indexable_terms = [
        mesh_indexable(t, index=index_name, doc_type=type_name) for t in terms
    ]

    successes, errors = bulk(es, indexable_terms)
    es.indices.refresh(index=index_name)


class TestSuggester(object):
    """Test Suggester."""

    def test_prefixing_query_matches(self, index_mesh_terms):
        query = "See"

        terms = suggest_terms(query)

        assert terms == [
            {
                'name': '(MeSH) Seed Bank',
                'value': {
                    'value': 'Seed Bank',
                    'source': 'MeSH'
                }
            },
        ]

    def test_nonprefixing_query_doesnt_match(self):
        query = "Te"

        terms = suggest_terms(query)

        assert terms == []

    def test_case_insensitive(self):
        query = "sEe"

        terms = suggest_terms(query)

        assert terms == [
            {
                'name': '(MeSH) Seed Bank',
                'value': {
                    'value': 'Seed Bank',
                    'source': 'MeSH'
                }
            },
        ]

    def test_space_separated_matches(self):
        query = "ba"

        terms = suggest_terms(query)

        assert terms == [
            {
                'name': '(MeSH) Seed Bank',
                'value': {
                    'value': 'Seed Bank',
                    'source': 'MeSH'
                }
            },
        ]

    def test_comma_separated_matches(self):
        query = "mu"

        terms = suggest_terms(query)

        assert terms == [
            {
                'name': '(MeSH) Abnormalities, Multiple',
                'value': {
                    'value': 'Abnormalities, Multiple',
                    'source': 'MeSH'
                }
            },
        ]

    def test_limit(self):
        query = "ab"

        terms = suggest_terms(query)

        assert 0 < len(terms) <= 5

        terms = suggest_terms(query, limit=3)

        assert 0 < len(terms) <= 3
