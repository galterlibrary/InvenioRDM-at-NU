"""Test MeSH extractor."""

from os.path import dirname, join, realpath

import pytest
from elasticsearch.helpers import bulk

from cd2h_repo_project.modules.terms.constants import FAST_SOURCE
from cd2h_repo_project.modules.terms.fast import FAST
from cd2h_repo_project.modules.terms.loaders import (
    INDEX, fast_indexable, mesh_indexable
)
from cd2h_repo_project.modules.terms.mesh import MeSH
from cd2h_repo_project.modules.terms.suggester import suggest_terms


@pytest.fixture(scope='module')
def index_terms(es):
    filename = 'descriptors_test_file.txt'
    filepath = join(dirname(realpath(__file__)), filename)
    terms = MeSH.load(filepath, filter='topics')
    indexable_terms = [mesh_indexable(t) for t in terms]

    filename = 'fast_test_file.nt'
    filepath = join(dirname(realpath(__file__)), filename)
    terms = FAST.load(filepath)
    indexable_terms.extend(fast_indexable(t) for t in terms)

    successes, errors = bulk(es, indexable_terms)
    es.indices.refresh(index=INDEX)


@pytest.mark.usefixtures("index_terms")
class TestSuggester(object):
    """Test Suggester."""

    def test_prefixing_query_matches(self):
        query = "See"

        terms = suggest_terms(query)

        assert terms == [
            {
                'name': '(MeSH) Seed Bank',
                'value': {
                    'value': 'Seed Bank',
                    'source': 'MeSH',
                    'id': 'FILL ME'  # TODO: Change id here
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
                    'source': 'MeSH',
                    'id': 'FILL ME'  # TODO: Change id here
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
                    'source': 'MeSH',
                    'id': 'FILL ME'  # TODO: Change id here
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
                    'source': 'MeSH',
                    'id': 'FILL ME'  # TODO: Change id here
                }
            },
        ]

    def test_limit(self):
        query = "ab"

        terms = suggest_terms(query)

        assert 0 < len(terms) <= 5

        terms = suggest_terms(query, limit=3)

        assert 0 < len(terms) <= 3

    def test_source_constrained(self):
        query = "Con"  # Congenital in MeSH, Control in FAST
        source = FAST_SOURCE

        terms = suggest_terms(query, source=source)

        assert terms == [
            {
                'name': '(FAST) Onions--Diseases and pests--Control',
                'value': {
                    'value': 'Onions--Diseases and pests--Control',
                    'source': source,
                    'id': 'FILL ME'  # TODO: Change id here
                }
            },
        ]
