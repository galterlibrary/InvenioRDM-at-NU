"""Test MeSH extractor."""

from os.path import dirname, join, realpath

from elasticsearch.helpers import bulk

from cd2h_repo_project.modules.terms.loaders import mesh_indexable


def test_indexable_single_term():
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


def test_indexable_spaced_term():
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


def test_indexable_comma_separated_term():
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


def test_bulk_loading(es, es_clear):
    index_name = 'terms'
    indexable_terms = [
        {
            '_index': index_name,
            '_type': 'term-v1.0.0',
            '_id': 'D000015',
            'source': 'MeSH',
            'value': 'Abnormalities, Multiple'
        }
    ]

    successes, errors = bulk(es, indexable_terms)

    assert successes == 1
    assert not errors

    es.indices.refresh(index=index_name)

    term = es.get(index=index_name, doc_type='term-v1.0.0', id='D000015')
    assert term['_source']['source'] == 'MeSH'
    assert term['_source']['value'] == 'Abnormalities, Multiple'
