from unittest.mock import Mock, patch

from cd2h_repo_project.modules.records.links import deposit_links_factory


def test_deposit_links_factory_contains_bucket(app, create_record):
    record = create_record()
    expected_bucket_id = record['_buckets']['deposit']

    with patch(
        'cd2h_repo_project.modules.records.links._deposit_links_factory',
        lambda x: {}
    ):
        links = deposit_links_factory(record.pid, record=record)

    assert links['bucket'] == '/api/files/' + expected_bucket_id


def test_deposit_links_factory_contains_html(app, create_record):
    record = create_record()
    expected_pid_value = record.pid.pid_value

    with patch(
        'cd2h_repo_project.modules.records.links._deposit_links_factory',
        lambda x: {}
    ):
        links = deposit_links_factory(record.pid, record=record)

    assert links['html'] == 'http://localhost/deposit/' + expected_pid_value