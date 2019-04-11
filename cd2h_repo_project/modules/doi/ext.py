# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Flask extension for DOI."""

from cd2h_repo_project.modules.doi.triggers import doi_minting_trigger
from cd2h_repo_project.modules.records.signals import menrva_record_published


class DigitalObjectIdentifier(object):
    """Digital Object Identifier extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        app.extensions['cd2h-doi'] = self
        menrva_record_published.connect(doi_minting_trigger)
