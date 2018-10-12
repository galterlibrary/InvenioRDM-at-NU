# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Data Model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Blueprint definitions."""

from __future__ import absolute_import, print_function

from flask import Blueprint, current_app

from .marshmallow.json import LICENSES

blueprint = Blueprint(
    'cd2hrepo_records',
    __name__,
    template_folder='templates',
    static_folder='static',
)
"""Blueprint used for loading templates and static assets

The sole purpose of this blueprint is to ensure that Invenio can find the
templates and static files located in the folders of the same names next to
this file.
"""


@blueprint.app_template_filter('extract_files')
def extract_files(deposit):
    """List dictionary representation of deposit files."""
    files_dicts = []

    # WARNING: Invenio passes us a dictionary in the new deposit page
    #          so we have to account for it.
    for f in getattr(deposit, "files", []):
        files_dicts.append({
            'key': f.key,
            'version_id': f.version_id,
            'checksum': f.file.checksum,
            'size': f.file.size,
            'completed': True,
            'progfiles_dictss': 100,
            'links': {
                'self': (
                    current_app.config['DEPOSIT_FILES_API'] +
                    u'/{bucket}/{key}?versionId={version_id}'.format(
                        bucket=f.bucket_id,
                        key=f.key,
                        version_id=f.version_id,
                    )),
            }
        })

    return files_dicts


@blueprint.app_template_filter('license_value_to_name')
def license_value_to_name(value):
    """Return license name of given license value."""
    for license in LICENSES:
        if license.value == value:
            return license.name
