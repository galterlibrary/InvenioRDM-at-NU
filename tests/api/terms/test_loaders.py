"""Test MeSH extractor."""

from os.path import dirname, join, realpath

import pytest
from elasticsearch.helpers import bulk

from cd2h_repo_project.modules.terms.loaders import (
    fast_indexable, mesh_indexable
)


class TestMeSHLoader(object):
    """Test MeSH loader."""

    def test_indexable_single_term(self):
        mesh_topic = {
            'MH': 'Filariasis',
            'DC': '1',
            'UI': 'D005368'
        }
        index_name = 'terms'
        type_name = 'term-v1.0.0'

        indexable_topic = mesh_indexable(
            mesh_topic, index=index_name, doc_type=type_name
        )

        assert indexable_topic == {
            '_index': index_name,
            '_type': type_name,
            '_id': 'D005368',
            'source': 'MeSH',
            'value': 'Filariasis',
            'suggest': ['Filariasis']
        }

    def test_indexable_spaced_term(self):
        mesh_topic = {
            'MH': 'Seed Bank',
            'DC': '1',
            'UI': 'D000068098'
        }
        index_name = 'terms'
        type_name = 'term-v1.0.0'

        indexable_topic = mesh_indexable(
            mesh_topic, index=index_name, doc_type=type_name
        )

        assert indexable_topic == {
            '_index': index_name,
            '_type': type_name,
            '_id': 'D000068098',
            'source': 'MeSH',
            'value': 'Seed Bank',
            'suggest': ['Seed Bank', 'Seed', 'Bank']
        }

    def test_indexable_comma_separated_term(self):
        mesh_topic = {
            'MH': 'Abnormalities, Multiple',
            'DC': '1',
            'UI': 'D000015'
        }
        index_name = 'terms'
        type_name = 'term-v1.0.0'

        indexable_topic = mesh_indexable(
            mesh_topic, index=index_name, doc_type=type_name
        )

        assert indexable_topic == {
            '_index': index_name,
            '_type': type_name,
            '_id': 'D000015',
            'source': 'MeSH',
            'value': 'Abnormalities, Multiple',
            'suggest': ['Abnormalities, Multiple', 'Abnormalities', 'Multiple']
        }

    # TODO: Check if es_clear necessary here
    def test_bulk_loading(self, es, es_clear):
        index_name = 'terms'
        indexable_terms = [
            {
                '_index': index_name,
                '_type': 'term-v1.0.0',
                '_id': 'D000015',
                'source': 'MeSH',
                'value': 'Abnormalities, Multiple',
                'suggest': [
                    'Abnormalities, Multiple', 'Abnormalities', 'Multiple'
                ]
            }
        ]

        successes, errors = bulk(es, indexable_terms)

        assert successes == 1
        assert not errors

        es.indices.refresh(index=index_name)

        term = es.get(index=index_name, doc_type='term-v1.0.0', id='D000015')
        assert term['_source']['source'] == 'MeSH'
        assert term['_source']['value'] == 'Abnormalities, Multiple'
        assert term['_source']['suggest'] == [
            'Abnormalities, Multiple',
            'Abnormalities',
            'Multiple'
        ]


class TestFASTLoader(object):
    """Test FAST loader."""

    @pytest.mark.parametrize('term, _id, suggest', [
        ('Glucagonoma', 943672, ['Glucagonoma']),
        ('Submarines (Ships)--Recognition', 1136653,
         ['Submarines (Ships)--Recognition', 'Submarines', 'Ships',
          'Recognition']),
        ('Onions--Diseases and pests--Control', 1045901,
         ['Onions--Diseases and pests--Control', 'Onions', 'Diseases',
          'pests', 'Control']),
        ('Architecture, Regency', 813916,
         ['Architecture, Regency', 'Architecture', 'Regency']),
        ('Eik\u014Dn (The Greek word)', 1749678,
         ['Eik\u014Dn (The Greek word)', 'Eik\u014Dn', 'Greek', 'word']),
    ])
    def test_indexable_variations(self, term, _id, suggest):
        fast_topic = {
            'identifier': _id,
            'prefLabel': term,
        }

        indexable_topic = fast_indexable(fast_topic)

        assert indexable_topic == {
            '_index': 'terms',
            '_type': 'term-v1.0.0',
            '_id': _id,
            'source': 'FAST',
            'value': term,
            'suggest': suggest
        }

    def test_bulk_loading(self, es, es_clear):
        index_name = 'terms'
        doc_type = 'term-v1.0.0'
        indexable_terms = [
            {
                '_index': index_name,
                '_type': doc_type,
                '_id': 1136653,
                'source': 'FAST',
                'value': 'Submarines (Ships)--Recognition',
                'suggest': [
                    'Submarines (Ships)--Recognition',
                    'Submarines',
                    'Ships',
                    'Recognition'
                ]
            }
        ]

        successes, errors = bulk(es, indexable_terms)

        assert successes == 1
        assert not errors

        es.indices.refresh(index=index_name)

        term = es.get(index=index_name, doc_type='term-v1.0.0', id=1136653)
        print("term from index", term)
        assert term['_source']['source'] == 'FAST'
        assert term['_source']['value'] == 'Submarines (Ships)--Recognition'
        assert term['_source']['suggest'] == [
            'Submarines (Ships)--Recognition',
            'Submarines',
            'Ships',
            'Recognition'
        ]
