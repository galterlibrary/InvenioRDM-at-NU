# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 - present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Term suggestion engine."""

from elasticsearch_dsl import Search
from invenio_search import current_search_client


def to_frontend_dict(es_suggestion):
    """Return JS-object-compatible Python dict from ES suggestion result."""
    source = es_suggestion['_source']['source']
    value = es_suggestion['_source']['value']

    return {
        'name': "({source}) {value}".format(source=source, value=value),
        # 'value' wrapper is needed bc frontend only accepts
        # 'name' and 'value' keys
        'value': {
            'value': value,
            'source': source
        }
    }


def suggest_terms(query, limit=5):
    """Return front-end consumable ES value suggestions from query."""
    result_bucket = 'terms'
    completion = {
        "field": "suggest",
        "size": limit
    }
    suggester = (
        Search(using=current_search_client, index='terms')
        .suggest(result_bucket, query, completion=completion)
    )

    result = suggester.execute()
    suggestions = result.suggest[result_bucket][0]['options']

    terms = [to_frontend_dict(s) for s in suggestions]

    return terms
