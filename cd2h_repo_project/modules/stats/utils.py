# -*- coding: utf-8 -*-
#
# This file is part of menRva.
# Copyright (C) 2018-present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Stats utility functions."""

from invenio_search import RecordsSearch


def put_record_stats_dict(record):
    """Insert stats dict in record dict."""
    # Just use all the STATS_QUERIES enabled via the config
    # Lifted and adapted from zenodo/modules/stats/utils.py
    stats = {}
    for query_name, cfg in stats_sources.items():
        try:
            query_cfg = current_stats.queries[query_name]
            query = query_cfg.query_class(**query_cfg.query_config)
            result = query.run(**cfg['params'])
            for dst, src in cfg['fields'].items():
                stats[dst] = result.get(src)
        except Exception:
            pass
    record['stats'] = stats


def get_record_stats_dict(record, raises=False):
    """Fetch record statistics from Elasticsearch."""
    try:
        documents = (
            RecordsSearch()
           # .source(include='_stats')  # only include "_stats" field
           .get_record(record.id)
           .execute()
        )
        print(__file__, "type(documents[0])", type(documents[0]))
        print(__file__, "dir(documents[0])", dir(documents[0]))
        print(__file__, "type(documents[0].meta)", type(documents[0].meta))
        print(__file__, "dir(documents[0].meta)", dir(documents[0].meta))
        print(__file__, "documents[0]._source", documents[0]._source)
        return documents[0]._stats.to_dict() if documents else {}
    except Exception:
        if raises:
            raise
        return {}
