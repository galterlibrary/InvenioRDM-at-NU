from unittest.mock import patch

from cd2h_repo_project.modules.records.links import deposit_links_api_factory


def test_deposit_links_api_factory_contains_bucket(app, create_record):
    record = create_record(published=False)
    expected_bucket_id = record['_buckets']['deposit']

    with patch(
        'cd2h_repo_project.modules.records.links._deposit_links_factory',
        lambda x: {}
    ):
        links = deposit_links_api_factory(record.pid, record=record)

    expected_link = 'http://localhost:5000/api/files/' + expected_bucket_id
    assert links['bucket'] == expected_link


def test_deposit_links_api_factory_contains_html(app, create_record):
    record = create_record(published=False)
    expected_pid_value = record.pid.pid_value

    with patch(
        'cd2h_repo_project.modules.records.links._deposit_links_factory',
        lambda x: {}
    ):
        links = deposit_links_api_factory(record.pid, record=record)

    expected_link = 'http://localhost:5000/deposit/' + expected_pid_value
    assert links['html'] == expected_link


def test_deposit_links_api_factory_accepts_no_record(app, create_record):
    # deposit_links_api_factory is called in Invenio without a record
    # for Header links which may or may not be a bug, but we need to sidestep
    # it
    record = create_record(published=False)

    with patch(
        'cd2h_repo_project.modules.records.links._deposit_links_factory',
        lambda x: {}
    ):
        links = deposit_links_api_factory(record.pid)

    assert links


def test_deposit_links_api_factory_contains_record_html(app, create_record):
    record = create_record(published=False)
    expected_pid_value = record.pid.pid_value

    with patch(
        'cd2h_repo_project.modules.records.links._deposit_links_factory',
        lambda x: {}
    ):
        links = deposit_links_api_factory(record.pid, record=record)

    expected_link = 'http://localhost:5000/records/' + expected_pid_value
    assert links['record_html'] == expected_link
