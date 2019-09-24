# -*- coding: utf-8 -*-
#
# This file is part of menRva.
# Copyright (C) 2018-present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test terms views.py"""

from cd2h_repo_project.modules.terms.views import serialize_terms_for_edit_ui


def test_serialize_terms_for_edit_ui(create_record):
    deposit = create_record(
        {
            'terms': [
                {'source': 'MeSH', 'value': 'Cognitive Neuroscience'},
                {'source': 'FAST', 'value': 'Border terrier'}
            ]
        },
        published=False
    )

    serialized_deposit = serialize_terms_for_edit_ui(deposit)

    assert 'terms' not in serialized_deposit
    assert serialized_deposit['mesh_terms'] == [
        {
            'data': {'source': 'MeSH', 'value': 'Cognitive Neuroscience'}
        }
    ]
    assert serialized_deposit['fast_terms'] == [
        {
            'data': {'source': 'FAST', 'value': 'Border terrier'}
        }
    ]


def test_serialize_terms_for_edit_ui_no_terms(create_record):
    deposit = create_record(published=False)

    serialized_deposit = serialize_terms_for_edit_ui(deposit)

    assert 'terms' not in serialized_deposit
    assert serialized_deposit['mesh_terms'] == []
    assert serialized_deposit['fast_terms'] == []
