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


def test_record_page_returns_200(client, record):
    """Test record view.

    We test views here even if the functionality is originally provided by
    cd2h-datamodel because:
    - cd2h-repo-project has the whole setup
    - cd2h-repo-project is the interface to the functionality in the end
    """
    response = client.get('/records/1')

    assert response.status_code == 200
    html_text = response.get_data(as_text=True)
    assert "A record" in html_text
    assert "An author" in html_text
    assert "A description" in html_text
