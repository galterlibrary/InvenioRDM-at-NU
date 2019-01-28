"""Deposit links factory."""

from __future__ import absolute_import, print_function

import os

from flask import current_app, request, url_for
from invenio_deposit.links import \
    deposit_links_factory as _deposit_links_factory


def deposit_links_api_factory(pid, **kwargs):
    """
    Return, from the API applicaton, the useful URLs related to this record.

    Adapted from https://github.com/zenodo/zenodo

    Note: Zenodo separates this functionality between API and UI so we do too.
    WARNING: **kwargs is necessary because Invenio does a backward
             compatibility check solely based on presence of **kwargs
             (invenio_records_rest/_compat.py). **kwargs indicates this is a
             "new style" link factory.

    :param pid: PersistentIdentifier of the record.
    :param kwargs: Keyword arguments, key 'record' and value Record is required
    """
    record = kwargs.get('record')
    links = _deposit_links_factory(pid)

    links['html'] = current_app.config['DEPOSIT_UI_ENDPOINT'].format(
        host=request.host,
        scheme=request.scheme,
        pid_value=pid.pid_value,
    )

    bucket_id = record.get('_buckets', {}).get('deposit') if record else None

    if bucket_id:
        # TODO: Make this a nice complete URL starting with `https://`
        #       so it is usable by API clients
        links['bucket'] = os.path.join('/api/files', bucket_id)

    return links


def deposit_links_ui_factory(pid, **kwargs):
    """
    Return, from the UI application, the useful URLs related to this record.

    Adapted from https://github.com/zenodo/zenodo

    Note: Zenodo separates this functionality between API and UI so we do too.
    WARNING: **kwargs is necessary because Invenio does a backward
             compatibility check solely based on presence of **kwargs
             (invenio_records_rest/_compat.py). **kwargs indicates this is a
             "new style" link factory.

    :param pid: PersistentIdentifier of the record.
    :param kwargs: Keyword arguments, key 'record' and value Record is required
    """
    record = kwargs.get('record')
    base_API_url = current_app.config['DEPOSIT_RECORDS_API'].format(
        pid_value=pid.pid_value)

    links = {
        'self': base_API_url,
        'html': url_for(
            'invenio_deposit_ui.{}'.format(pid.pid_type),
            pid_value=pid.pid_value
        ),
        'bucket': (
            current_app.config['DEPOSIT_FILES_API'] +
            '/{0}'.format(record.files.bucket.id)
        ),
        'discard': base_API_url + '/actions/discard',
        'edit': base_API_url + '/actions/edit',
        'publish': base_API_url + '/actions/publish',
        # TODO: Uncomment when we get to versioning
        # 'newversion': base_API_url + '/actions/newversion',
        # 'registerconceptdoi': base_API_url + '/actions/registerconceptdoi',
        'files': base_API_url + '/files',
    }

    return links
