# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Data Model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Flask extension for CD2H Data Model."""

from __future__ import absolute_import, print_function

from invenio_indexer.signals import before_record_index

from .index_hooks import before_deposit_index_hook


class Records(object):
    """CD2H Records Model extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        app.extensions['cd2h-records'] = self
        before_record_index.connect(
            before_deposit_index_hook, sender=app, weak=False
        )
