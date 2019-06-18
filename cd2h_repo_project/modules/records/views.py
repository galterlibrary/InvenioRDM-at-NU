# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Data Model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Blueprint definitions."""

from collections import defaultdict

from flask import Blueprint, current_app, redirect, render_template, url_for
from flask_menu import register_menu
from invenio_db import db
from invenio_records_ui.signals import record_viewed

from cd2h_repo_project.modules.records.links import deposit_links_ui_factory
from cd2h_repo_project.modules.records.marshmallow.json import LICENSES
from cd2h_repo_project.modules.records.permissions import (
    EditMetadataPermission, RecordPermissions
)

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


@blueprint.app_template_filter('get_links')
def get_links(pid, record):
    """Return dictionary of related links."""
    return deposit_links_ui_factory(pid, record=record)


def edit_view_method(pid, record, template=None):
    """View method for updating record.

    Sends ``record_viewed`` signal and renders template.

    :param pid: PID object ('depid'-type PID).
    :param record: Record object (Deposit API).
    :param template: Template to render.

    Taken from zenodo/zenodo
    """
    # Put deposit in edit mode if not already.
    if record['_deposit']['status'] != 'draft':
        record = record.edit()
        db.session.commit()

    record_viewed.send(
        current_app._get_current_object(),
        pid=pid,
        record=record,
    )

    return render_template(template, pid=pid, record=record)


@blueprint.app_template_filter('has_edit_metadata_permission')
def has_edit_metadata_permission(user, record):
    """Return boolean whether user can update record."""
    return EditMetadataPermission(user, record).can()


@blueprint.app_template_filter('to_available_options')
def to_available_options(sort_options):
    """Create JSON-compatible sort options dict for Invenio-Search-JS.

    :param sort_options: A dictionary of sort identifier as keys and sort
                         configuration as values.
                         See RECORDS_REST_SORT_OPTIONS[<index>].
    :returns: A JSON compatible dict of sorting options for a <select> tag.
    """
    return {
        'options': [
            {'value': identifier, 'title': configuration['title']}
            for identifier, configuration in
            sorted(
                sort_options.items(),
                key=lambda id_conf: id_conf[1].get('order', 0)
            )
        ]
    }


@blueprint.app_template_filter('permissions_to_label_css')
def permissions_to_label_css(permissions):
    """Return Bootstrap label class qualifier corresponding to permissions.

    Return <this> in class="label label-<this>".
    """
    if permissions.startswith('all_'):
        return 'success'
    elif permissions.startswith('restricted_'):
        return 'warning'
    else:
        return 'danger'


@blueprint.app_template_filter('permissions_to_access_name')
def permissions_to_access_name(permissions):
    """Return 'Open/Restricted/Private Access' corresponding to permissions."""
    if permissions.startswith('all_'):
        return 'Open Access'
    elif permissions.startswith('restricted_'):
        return 'Restricted Access'
    else:
        return 'Private Access'


@blueprint.app_template_filter('is_private')
def is_private(record):
    """Return True/False corresponding to private or not."""
    return RecordPermissions.is_private(record)
