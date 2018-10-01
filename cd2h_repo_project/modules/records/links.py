"""Deposit links factory."""

from __future__ import absolute_import, print_function

import os

from flask import current_app, request
from invenio_deposit.links import \
    deposit_links_factory as _deposit_links_factory


def deposit_links_factory(pid, **kwargs):
    """
    Deposit links factory.

    Adapted from https://github.com/zenodo/zenodo
    """
    links = _deposit_links_factory(pid)

    links['html'] = current_app.config['DEPOSIT_UI_ENDPOINT'].format(
        host=request.host,
        scheme=request.scheme,
        pid_value=pid.pid_value,
    )

    bucket_id = kwargs.get('record', {}).get('_buckets', {}).get('deposit')

    if bucket_id:
        # TODO: Make this a nice complete URL starting with `https://`
        #       so it is usable by API clients
        links['bucket'] = os.path.join('/api/files', bucket_id)

    return links
