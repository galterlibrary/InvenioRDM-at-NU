# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Views tests.

We have simple, very high-level, view tests here even if the functionality is
originally provided by another module because:
- this project has the whole setup
- this project is the interface to the functionality in the end
"""

from __future__ import absolute_import, print_function

import re

from flask import url_for
from flask_menu import current_menu
from flask_security import login_user, url_for_security

from utils import login_request_and_session

# WARNING: the client fixture adds a ~5sec (large) startup overhead to tests


def test_ping(client):
    """Test the ping view."""
    resp = client.get(url_for('cd2h_repo_project.ping'))

    assert resp.status_code == 200
    assert resp.get_data(as_text=True) == 'OK'


# Front Page
def test_front_page_has_only_one_search_bar_and_one_catalog_link(client):
    response = client.get('/')
    html_text = response.get_data(as_text=True)
    invenio_search_bar = re.findall('<invenio-search-bar', html_text)
    role_search = re.findall('role="search"', html_text)
    catalog_links = re.findall('/deposit/new', html_text)

    assert not invenio_search_bar
    assert len(role_search) == 1
    assert len(catalog_links) == 1


# Record Page
def test_record_page_returns_200(client, create_record):
    """Test record view."""
    record = create_record()

    # WARNING: In invenio record.id != record['id']
    response = client.get(
        url_for('invenio_records_ui.recid', pid_value=record['id']))
    html_text = response.get_data(as_text=True)

    assert response.status_code == 200
    html_text = response.get_data(as_text=True)
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


# Search Page
def test_search_page_returns_200(client):
    """Test search page.
    """
    response = client.get('/search')
    html_text = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "<h1>Search</h1>" in html_text
    assert '</invenio-search-bar>' in html_text


def test_search_page_has_only_one_search_bar(client):
    response = client.get('/search')
    html_text = response.get_data(as_text=True)
    invenio_search_bar = re.findall('<invenio-search-bar', html_text)
    role_search = re.findall('role="search"', html_text)

    assert len(invenio_search_bar) == 1
    assert not role_search


# Deposit Page
def test_deposits_page_requires_login(client, create_user):
    user = create_user()
    deposits_page_url = url_for('invenio_deposit_ui.index')

    response = client.get(deposits_page_url)

    assert response.status_code == 302
    assert response.location.endswith('login/?next=%2Fdeposit')

    login_request_and_session(user, client)

    response = client.get(deposits_page_url)

    assert response.status_code == 200


def test_deposits_page_has_search_bar(client, create_user):
    user = create_user()
    login_request_and_session(user, client)

    response = client.get('/deposit/new')
    html_text = response.get_data(as_text=True)
    invenio_search_bar = re.findall('<invenio-search-bar', html_text)
    role_search = re.findall('role="search"', html_text)

    assert len(invenio_search_bar) == 0
    assert len(role_search) == 1


# Other
def test_user_dropdown_contains_deposits_link(appctx):
    assert 'deposits' in current_menu.submenu('settings')._child_entries
