# -*- coding: utf-8 -*-
#
# This file is part of menRva.
# Copyright (C) 2018-present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Statistics Tests"""

from datetime import date

from elasticsearch_dsl import Search
from flask import current_app, url_for
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_ui.signals import record_viewed
from invenio_stats.tasks import aggregate_events, process_events
from invenio_search import current_search, current_search_client

from cd2h_repo_project.modules.stats.utils import get_record_stats_dict


def test_record_page_shows_statistics(client, create_record):
    record = create_record()

    response = client.get(
        url_for('invenio_records_ui.recid', pid_value=record['id'])
    )
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


def test_record_viewed_signal_has_view_receiver(client, create_record):
    receiver_names = {v.name for v in record_viewed.receivers.values()}

    assert 'record-view' in receiver_names


def test_process_events_scheduled(config):
    assert (
        config['CELERY_BEAT_SCHEDULE']['stats-process-events']['task'] ==
        'invenio_stats.tasks.process_events'
    )


def test_process_record_view_events_indexes_stats_event(
        create_record, es_clear, message_queues):
    """Tests STATS_EVENTS configuration."""
    es = es_clear
    record = create_record()
    pid = PersistentIdentifier.get(
        record['_deposit']['pid']['type'],
        record['_deposit']['pid']['value'],
    )
    with current_app.test_request_context():
        record_viewed.send(
            current_app._get_current_object(),
            pid=pid,
            record=record,
        )
    index = 'events-stats-record-view'

    process_events(['record-view'])
    current_search.flush_and_refresh(index=index)

    search = Search(using=es, index=index)
    assert search.count() == 1
    doc = search.execute()[0]
    # These tests are less about values than about presence.
    # The values are provided and tested by 3rd party.
    assert doc['pid_type'] == pid.pid_type
    assert doc['pid_value'] == pid.pid_value
    assert doc['visitor_id']
    assert doc['referrer'] is None
    assert doc['record_id'] == str(record.id)
    assert not doc['is_robot']
    assert doc['unique_session_id']
    assert doc['timestamp']
    assert doc['unique_id']


def test_aggregate_events_scheduled(config):
    assert (
        config['CELERY_BEAT_SCHEDULE']['stats-aggregate-events']['task'] ==
        'invenio_stats.tasks.aggregate_events'
    )


def test_aggregate_record_view_stats_event_indexes_aggregate_event(
        create_record, es_clear, message_queues):
    """Tests STATS_AGGREGATIONS configuration."""
    record = create_record()
    pid = PersistentIdentifier.get(
        record['_deposit']['pid']['type'],
        record['_deposit']['pid']['value'],
    )
    with current_app.test_request_context():
        record_viewed.send(
            current_app._get_current_object(),
            pid=pid,
            record=record,
        )
    process_events(['record-view'])
    print("aliases", current_search_client.indices.get_alias('*'))
    current_search.flush_and_refresh(index='events-stats-record-view')
    aggr_index = 'stats-record-view'
    es = es_clear

    aggregate_events(['record-view-agg'])
    current_search.flush_and_refresh(index=aggr_index)

    search = Search(using=es, index=aggr_index)
    assert search.count() == 1
    doc = search.execute()[0]
    # These tests are less about values than about presence.
    # The values are provided and tested by 3rd party.
    assert doc['timestamp']
    assert doc['count'] == 1
    assert doc['unique_count'] == 1
    assert doc['record_id'] == str(record.id)
    assert doc['collection']


def test_put_record_stats_dict_called_at_es_indexing_time():
    # index
    # check values are given - 0 views...
    assert False


def test_put_record_stats_dict():
    assert False


def test_get_record_stats_dict_returns_relevant_stats(es_clear):
    """Tests STATS_QUERIES configuration."""
    # More direct version of this: just plce a stats_event in the
    # aggregator index directly
    # with current_app.test_request_context():
    #     record_viewed.send(
    #         current_app._get_current_object(),
    #         pid=pid,
    #         record=record,
    #     )
    # TODO: FIX: this should not be needed
    # suffix = date.today().strftime('%Y-%m-%d')
    # index = 'events-stats-record-view-{}'.format(suffix)
    # process_events(['record-view'])
    # current_search.flush_and_refresh(index=index)
    # aggregate_events(
    #     ['record-view-agg', 'record-view-all-versions-agg',
    #      'record-download-agg', 'record-download-all-versions-agg'])
    # current_search.flush_and_refresh(index='stats-*')

    # search = Search(using=es, index=index)
    # assert search.count() == 1
    # doc = search.execute()[0]
    # # These tests are less about values than about presence.
    # # The values are provided and tested by 3rd party.
    # assert doc['pid_type'] == pid.pid_type
    # assert doc['pid_value'] == pid.pid_value
    # assert doc['visitor_id']
    # assert doc['referrer'] is None
    # assert doc['record_id'] == str(record.id)
    # assert not doc['is_robot']
    # assert doc['unique_session_id']
    # assert doc['timestamp']
    # assert doc['unique_id']
    # stats = get_record_stats_dict(record, True)

    # assert stats['timestamp']
    # assert stats['record_id'] == 1
    # assert stats['pid_type'] == 1
    # assert stats['pid_value'] == 1
    # assert stats['is_robot'] == 1
    # assert stats['visitor_id'] == 1
    # assert stats['unique_session_id'] == 1
    assert False


# Do the same thing for download events
def test_process_file_download_events_indexes_stats_event(es_clear):
    # process_events(['file-download'])
    assert False
