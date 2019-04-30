# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 - present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""MeSH loaders."""


def indexable(mesh_topic, index, doc_type):
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
