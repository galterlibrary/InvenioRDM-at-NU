# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Views tests."""

from __future__ import absolute_import, print_function

from flask import url_for


def test_ping(client):
    """Test the ping view."""
    resp = client.get(url_for('cd2h_repo_project.ping'))
    assert resp.status_code == 200
    assert resp.get_data(as_text=True) == 'OK'
