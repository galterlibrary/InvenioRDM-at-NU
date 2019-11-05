# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Flask extension for MODULE NAME."""

from __future__ import absolute_import, print_function


class CHANGE_ME_TO_MODULE_NAME(object):
    """MODULE NAME extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        app.extensions['cd2h-module-name'] = self
