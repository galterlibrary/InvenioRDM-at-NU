# -*- coding: utf-8 -*-
#
# This file is part of menRva.
# Copyright (C) 2018-present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record Page views tests."""

from flask import current_app, request, url_for

from utils import login_request_and_session


# Record Page
def test_record_page_returns_200(client, create_record):
    record = create_record()

    # WARNING: In invenio record.id != record['id']
    response = client.get(
        url_for('invenio_records_ui.recid', pid_value=record['id']))
    html_text = response.get_data(as_text=True)

    assert response.status_code == 200
    print(html_text)  # Kept for nicer test experience
    assert "A title" in html_text
    assert "Author, An" in html_text
    assert "A description" in html_text
    assert "Other / Other" in html_text
    assert "MIT License" in html_text


def test_record_page_shows_files(client, create_record):
    record = create_record({'_files': [{'key': 'fileA.png', 'size': 8889}]})

    response = client.get(
        url_for('invenio_records_ui.recid', pid_value=record['id']))
    html_text = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "fileA.png" in html_text
    assert "8.9 kB" in html_text
    assert (
        'href="/records/{}/files/fileA.png?download=1"'.format(record['id'])
        in html_text
    )


def test_record_page_shows_edit_action_if_permitted(
        client, create_record, create_user):
    user = create_user()
    owned_record = create_record({'_deposit': {'owners': [user.id]}})
    not_owned_record = create_record()
    login_request_and_session(user, client)

    response = client.get('/records/{}'.format(owned_record['id']))
    page = response.get_data(as_text=True)
    html_tree = html.fromstring(page)
    edit_links = html_tree.cssselect('a#edit-action')

    assert len(edit_links) == 1
    pid_value = owned_record['_deposit']['id']
    assert edit_links[0].get('href') == '/deposit/{}'.format(pid_value)

    response = client.get('/records/{}'.format(not_owned_record['id']))
    html_tree = html.fromstring(response.get_data(as_text=True))
    edit_links = html_tree.cssselect('a#edit-action')

    assert len(edit_links) == 0
