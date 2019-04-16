"""MeSH views."""
from flask import Blueprint, jsonify, request
from flask_security import login_required

from .suggester import suggest_terms

blueprint = Blueprint(
    'menrva_mesh',
    __name__,
    url_prefix='/mesh',
)


@blueprint.route('/_suggest', methods=['GET'])
@login_required
def suggest():
    """Suggest a MeSH keyword on the deposit form."""
    q = request.args.get('q', '')
    limit = request.args.get('limit', type=int)

    terms = suggest_terms(q, limit=limit) if limit else suggest_terms(q)

    response = {'terms': terms}

    return jsonify(response)
