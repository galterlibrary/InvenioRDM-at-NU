# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Data Model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Blueprint definitions."""
from datetime import datetime, timedelta

from flask import Blueprint, url_for

from .links import doi_url_for

blueprint = Blueprint(
    'cd2hrepo_doi',
    __name__,
    template_folder='templates',
    static_folder='static',
)
"""Blueprint used for loading templates and static assets

The sole purpose of this blueprint is to ensure that Invenio can find the
templates and static files located in the folders of the same names next to
this file.
"""


@blueprint.app_template_filter('to_doi_field')
def to_doi_field(record):
    """Generate the DOI field."""
    doi_value = record.get('doi')
    if doi_value:
        doi_url = doi_url_for(doi_value)
        return '<a href="{0}">{0}</a>'.format(doi_url)
    elif datetime.utcnow() < record.model.created + timedelta(hours=24):
        return 'Minting the DOI... (refresh to update)'
    else:
        return (
            'There was an issue minting the DOI. '
            '<a href="{}">Contact us</a>.'.format(
                url_for('contact_us.contact_us'))
        )
