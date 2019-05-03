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

from .suggester import suggest_terms

blueprint = Blueprint(
    'menrva_terms',
    __name__,
    url_prefix='/terms',
)


@blueprint.route('/mesh/_suggest', methods=['GET'])
@login_required
def mesh_suggest():
    """Suggest a MeSH keyword on the deposit form."""
    q = request.args.get('q', '')
    limit = request.args.get('limit', type=int)

    terms = suggest_terms(q, limit=limit) if limit else suggest_terms(q)

    response = {'terms': terms}

    return jsonify(response)
