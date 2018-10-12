# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Views tests.

We have simple, very high-level, view tests here even if the functionality is
originally provided by cd2h-datamodel (or another module) because:
- cd2h-repo-project has the whole setup
- cd2h-repo-project is the interface to the functionality in the end

"""

from __future__ import absolute_import, print_function

from flask import url_for


def test_ping(client):
    """Test the ping view."""
    resp = client.get(url_for('cd2h_repo_project.ping'))

    assert resp.status_code == 200
    assert resp.get_data(as_text=True) == 'OK'


def test_record_page_returns_200(client, create_record):
    """Test record view."""
    record = create_record()

    # WARNING: In invenio record.id != record['id']
    response = client.get(
        url_for('invenio_records_ui.recid', pid_value=record['id']))
    html_text = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "A title" in html_text
    assert "An author" in html_text
    assert "A description" in html_text
    assert "MIT License" in html_text


def test_record_page_shows_files(client, create_record):
    record = create_record({'_files': [{'key': 'fileA.png', 'size': 8889}]})

    response = client.get(
        url_for('invenio_records_ui.recid', pid_value=record['id']))
    html_text = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "fileA.png" in html_text
    assert "8.9 kB" in html_text


def test_search_page_returns_200(client):
    """Test search page.
    """
    response = client.get('/search')
    html_text = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "<h1>Search</h1>" in html_text
    assert '</invenio-search-bar>' in html_text
