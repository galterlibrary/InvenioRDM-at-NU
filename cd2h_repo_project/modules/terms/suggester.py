# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 - present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Term suggestion engine."""

from elasticsearch_dsl import Search
from invenio_search import current_search_client

from cd2h_repo_project.modules.terms.constants import SOURCES


def to_frontend_dict(es_suggestion):
    """Return JS-object-compatible Python dict from ES suggestion result.

    The frontend expects 2 fields, 'name' (human readable value) and 'value'
    (machine/backend value).
    TODO: Use id from es_suggestion
    """
    source = es_suggestion['_source']['source']
    value = es_suggestion['_source']['value']

    return {
        'name': "({source}) {value}".format(source=source, value=value),
        'value': {
            'value': value,
            'source': source,
            'id': 'FILL ME'
        }
    }


def suggest_terms(query, source=None, limit=5):
    """Return front-end consumable ES value suggestions from query.

    For now, only allow one `source` or None (all sources).
    """
    result_bucket = 'terms'
    completion = {
        "field": "suggest",
        "size": limit,
        "contexts": {
            "source_filter": [s for s in SOURCES if s == source or not source]
        }
    }
    suggester = (
        Search(using=current_search_client, index='terms')
        .suggest(result_bucket, query, completion=completion)
    )

    result = suggester.execute()
    suggestions = result.suggest[result_bucket][0]['options']

    terms = [to_frontend_dict(s) for s in suggestions]

    return terms
