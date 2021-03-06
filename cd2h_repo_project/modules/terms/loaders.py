# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 - present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Terms loaders."""
import re

INDEX = 'terms-term-v1.0.0'
DOC_TYPE = 'term-v1.0.0'


def mesh_indexable(mesh_topic, index=INDEX, doc_type=DOC_TYPE):
    """Return an ES indexable dict from MeSH dict."""
    mesh_term = mesh_topic['MH']

    suggest = [mesh_term]
    if ' ' in mesh_term:
        suggest.extend(mt.strip('.,') for mt in mesh_term.split())

    indexable_topic = {
        '_index': index,
        '_type': doc_type,
        '_id': mesh_topic['UI'],
        'source': 'MeSH',
        'value': mesh_term,
        'suggest': suggest
    }

    return indexable_topic


def _fast_suggest(term):
    """Return [] of suggestions derived from term.

    This list is generated by removing punctuation and some stopwords.
    """
    suggest = [term]

    def valid(subterm):
        """Ensure subterm is valid."""
        # poor man stopwords collection
        stopwords = ['and', 'the', 'in', 'of']
        return subterm and subterm.lower() not in stopwords

    subterms = [st for st in re.split(r'\W', term) if valid(st)]
    if len(subterms) > 1:
        suggest.extend(subterms)

    return suggest


def fast_indexable(topic, index=INDEX, doc_type=DOC_TYPE):
    """Return an ES indexable dict from FAST dict.

    FAST dict have this interface:

    {
        'identifier': <_id>
        'prefLabel': <value>
    }
    """
    term = topic['prefLabel']

    suggest = _fast_suggest(term)

    indexable_topic = {
        '_index': index,
        '_type': doc_type,
        '_id': topic['identifier'],
        'source': 'FAST',
        'value': term,
        'suggest': suggest
    }

    return indexable_topic
