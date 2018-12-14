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

from flask import current_app, request, url_for
from flask_login import current_user
from flask_menu import current_menu
from flask_security import url_for_security
from lxml import html

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


# Activity Feed Page
def test_activity_feed_page_requires_login(client, create_user):
    user = create_user()
    activity_feed_url = '/account'

    response = client.get(activity_feed_url)

    assert response.status_code == 302
    assert response.location.endswith('login/?next=%2Faccount')

    login_request_and_session(user, client)

    response = client.get(activity_feed_url)

    assert response.status_code == 200


def test_account_page_menu_contains_desired_links(
        client, create_user, admin_user):
    # NOTE: admin_user is needed because of a quirk in invenio-admin.
    #       A PR: https://github.com/inveniosoftware/invenio-admin/pull/67
    #       has been submitted.
    user = create_user()
    login_request_and_session(user, client)

    response = client.get('/account')
    html_tree = html.fromstring(response.get_data(as_text=True))
    links = {
        a.get('href') for a in html_tree.cssselect('ul.list-group a')
    }

    assert links == {
        '/account',
        '/deposits',
        '/account/settings/profile/',
        '/account/settings/security/',
        '/account/settings/applications/',
    }


# Contact Us Page
def test_missing_data_returns_errors(client):
    response = client.post(
        '/contact-us',
        data={
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'subject': 'A subject'
            # missing 'message'
        },
        follow_redirects=True
    )
    html_tree = html.fromstring(response.get_data(as_text=True))
    error_li = html_tree.cssselect('ul.errors li')[0]

    assert error_li.text_content() == "This field is required."
    assert request.path == '/contact-us'


def test_successful_form_completion_redirects_to_front_page_w_flash(client):
    response = client.post(
        '/contact-us',
        data={
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'subject': 'A subject',
            'message': 'A message'
        },
        follow_redirects=True
    )
    html_tree = html.fromstring(response.get_data(as_text=True))
    alert = html_tree.cssselect('div.alert-success')[0]

    assert request.path == '/'
    assert (
        "Thank you for contacting us. We will be in touch soon!" in
        alert.text_content()
    )


def test_successful_form_completion_sends_support_email(client):
    with current_app.extensions['mail'].record_messages() as outbox:
        response = client.post(
            '/contact-us',
            data={
                'name': 'Jane Smith',
                'email': 'jane@example.com',
                'subject': 'A subject',
                'message': 'A message\n<script>alert("annoying")</script>'
            },
            follow_redirects=True
        )

        assert len(outbox) == 2  # Includes the confirmation email. See below.
        support_email = outbox[0]
        assert support_email.sender == 'Jane Smith <jane@example.com>'
        sitename = current_app.config['THEME_SITENAME']
        assert support_email.recipients == [(sitename, 'digitalhub@northwestern.edu')]  # noqa
        assert support_email.subject == '[{} - Contact Us]: A subject'.format(sitename)  # noqa
        assert support_email.reply_to == ('Jane Smith', 'jane@example.com')
        assert 'Jane Smith <jane@example.com>' in support_email.body
        assert 'A message' in support_email.body


def test_successful_form_completion_sends_confirmation_email(client):
    with current_app.extensions['mail'].record_messages() as outbox:
        response = client.post(
            '/contact-us',
            data={
                'name': 'Jane Smith',
                'email': 'jane@example.com',
                'subject': 'A subject',
                'message': 'A message <script>alert("annoying")</script>'
            },
            follow_redirects=True
        )

        assert len(outbox) == 2  # Includes the support email. See above.
        confirmation_email = outbox[1]
        sitename = current_app.config['THEME_SITENAME']
        assert confirmation_email.sender == '{} <digitalhub@northwestern.edu>'.format(sitename)  # noqa
        assert confirmation_email.recipients == [
            ('Jane Smith', 'jane@example.com')
        ]
        assert confirmation_email.subject == '[{} - Contact Us] Confirmation'.format(sitename)  # noqa
        assert (
            'Thank you for contacting us at {}.'.format(sitename)
            in confirmation_email.body
        )


# Other
def test_user_dropdown_contains_desired_links(client, create_user):
    user = create_user()
    login_request_and_session(user, client)

    response = client.get('/')
    html_tree = html.fromstring(response.get_data(as_text=True))
    links = {
        a.get('href') for a in html_tree.cssselect('ul.dropdown-menu li a')
    }

    assert links == {
        '/account',
        '/deposits',
        '/account/settings/profile/',
        '/logout/'
    }
