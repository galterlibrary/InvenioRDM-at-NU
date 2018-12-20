from cd2h_repo_project.modules.records.links import deposit_links_ui_factory


def test_deposit_links_ui_factory_contains_all_links(app, create_record):
    record = create_record()
    expected_pid_value = record.pid.pid_value
    expected_bucket_id = record['_buckets']['deposit']

    links = deposit_links_ui_factory(record.pid, record=record)

    assert links['self'] == '/api/deposits/{}'.format(expected_pid_value)
    assert links['html'] == '/deposit/{}'.format(expected_pid_value)
    assert links['bucket'] == '/api/files/{}'.format(expected_bucket_id)
    for action in ['discard', 'edit', 'publish']:
        assert links[action] == '/api/deposits/{}/actions/{}'.format(
            expected_pid_value, action)
    assert links['files'] == '/api/deposits/{}/files'.format(
        expected_pid_value)
