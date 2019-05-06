# -*- coding: utf-8 -*-
#
# This file is part of menRva.
# Copyright (C) 2018-present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Terms views."""
from flask import Blueprint, jsonify, request
from flask_security import login_required

from .constants import FAST_SOURCE, MESH_SOURCE
from .suggester import suggest_terms

blueprint = Blueprint(
    'menrva_terms',
    __name__,
    url_prefix='/terms',
)


def suggest(source=None):
    """Return term suggestions."""
    q = request.args.get('q', '')
    limit = request.args.get('limit', type=int)

    if limit:
        terms = suggest_terms(q, source=source, limit=limit)
    else:
        terms = suggest_terms(q, source=source)

    response = {'terms': terms}

    return jsonify(response)


@blueprint.route('/_suggest', methods=['GET'])
@login_required
def all_suggest():
    """Suggest keywords from *all* sources."""
    return suggest()


@blueprint.route('/mesh/_suggest', methods=['GET'])
@login_required
def mesh_suggest():
    """Suggest MeSH keywords."""
    return suggest(MESH_SOURCE)


@blueprint.route('/fast/_suggest', methods=['GET'])
@login_required
def fast_suggest():
    """Suggest FAST keywords."""
    return suggest(FAST_SOURCE)
