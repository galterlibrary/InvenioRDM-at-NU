# -*- coding: utf-8 -*-
#
# This file is part of menRva.
# Copyright (C) 2018-present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Statistics Tests"""

from flask import url_for

from invenio_records_ui.signals import record_viewed


def test_record_page_returns_200(client, create_record):
    record = create_record()

    response = client.get(
        url_for('invenio_records_ui.recid', pid_value=record['id']))
    html_text = response.get_data(as_text=True)

    assert response.status_code == 200
    print(html_text)  # Kept for nicer test experience
    assert "0 views" in html_text
    assert "0 downloads" in html_text


def test_viewing_a_record_triggers_record_viewed_signal(client, create_record):
    record_ = create_record()
    signal_sent = False

    def has_signal_been_sent(sender, pid=None, record=None):
        nonlocal signal_sent
        signal_sent = True
        assert pid.pid_value == record['id']
        assert record == record_

    with record_viewed.connected_to(has_signal_been_sent):
        client.get(
            url_for('invenio_records_ui.recid', pid_value=record_['id'])
        )

    assert signal_sent
