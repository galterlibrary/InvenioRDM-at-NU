from io import BytesIO
from unittest.mock import Mock

import jsonschema
import pytest
from invenio_files_rest.models import Bucket
from invenio_pidstore import current_pidstore
from invenio_records.models import RecordMetadata
from invenio_records_files.models import RecordsBuckets

from cd2h_repo_project.modules.records.api import (
    Deposit, FileObject, RecordType
)


def test_deposit_create_creates_recordsbuckets(locations):
    assert RecordsBuckets.query.first() is None
    assert RecordMetadata.query.first() is None
    assert Bucket.query.first() is None

    deposit = Deposit.create({})

    record_bucket = RecordsBuckets.query.first()
    record = RecordMetadata.query.first()
    bucket = Bucket.query.first()
    assert record_bucket
    assert record_bucket.record == record
    assert record_bucket.bucket == bucket


def test_deposit_create_fills_data(locations):
    data = {}

    deposit = Deposit.create(data)

    assert data['_buckets']['deposit']


def test_deposit_publish_calls_configured_minters(
        config, create_record, mocker):
    mocked_mint_recid_pid = mocker.patch(
        'cd2h_repo_project.modules.records.minters.mint_recid_pid'
    )
    mocked_mint_doi_pid = mocker.patch(
        'cd2h_repo_project.modules.records.minters.mint_doi_pid'
    )
    deposit = create_record(published=False)

    assert config['DEPOSIT_PID_MINTER'] == 'cd2h_recid'

    # We expect deposit.publish to fail here because we patched it
    # What is important is that the patches were called
    with pytest.raises(jsonschema.exceptions.ValidationError):
        deposit.publish()

    assert mocked_mint_recid_pid.called
    assert mocked_mint_doi_pid.called


def test_deposit_publish_sets_appropriate_types(locations):
    deposit = Deposit.create({})

    deposit_record = deposit.publish()
    pid, published_record = deposit_record.fetch_published()

    assert deposit_record['type'] == RecordType.draft.value
    assert published_record['type'] == RecordType.published.value


def test_deposit_edit_sets_type(create_record):
    deposit = create_record(published=False)
    deposit.publish()  # to set deposit's _deposit.status = 'published'

    draft_record = deposit.edit()

    assert draft_record['type'] == RecordType.draft.value


def test_deposit_edit_sets_revision_id(create_record):
    deposit = create_record(published=False)
    deposit.publish()

    draft_record = deposit.edit()

    assert draft_record['_deposit']['pid']['revision_id'] == 1


def test_fetch_deposit(create_record):
    unpublished_record = create_record(published=False)
    unpublished_record.publish()
    _, published_record = unpublished_record.fetch_published()

    _, deposit = Deposit.fetch_deposit(published_record)

    assert unpublished_record == deposit


def test_clear_deposit_preserves_appropriate_fields(create_record):
    record = create_record()
    _, deposit = Deposit.fetch_deposit(record)
    # TODO: Update with fields not available on the deposit form
    fields_to_preserve = ['_buckets', '_deposit', 'id', 'type', 'doi']

    # Pre-condition
    assert set(fields_to_preserve) == set(Deposit.NON_FORM_FIELDS_TO_PRESERVE)
    preserved = {}
    assert deposit['$schema']  # Example of field not to preserve
    for field in fields_to_preserve:
        assert field in deposit
        preserved[field] = deposit[field]

    deposit['_deposit']['status'] = 'draft'  # Needed to clear
    cleared_deposit = deposit.clear()

    # Post-condition
    assert '$schema' not in deposit
    for field in fields_to_preserve:
        assert preserved[field] == cleared_deposit[field]


def test_fileobject_dumps_serializes_filetype(create_record):
    deposit = create_record(published=False)

    # Normal case
    # Easiest way to create a FileObject
    deposit.files['test.TXT'] = BytesIO(b'Hello world!')
    file_object = deposit.files['test.TXT']

    data = file_object.dumps()

    assert isinstance(file_object, FileObject)
    assert data['type'] == 'txt'

    # No file extension case
    deposit.files['testfile'] = BytesIO(b'Hello world!')
    file_object = deposit.files['testfile']

    data = file_object.dumps()

    assert data['type'] == 'other'

    # Multiple extensions case
    deposit.files['test.tar.gz'] = BytesIO(b'Hello world!')
    file_object = deposit.files['test.tar.gz']

    data = file_object.dumps()

    assert data['type'] == 'gz'


def test_publish_edit_publish_flow(create_record):
    # This flow is often problematic so we test it explicitly
    # TODO: See if this helps in the long term
    deposit = create_record(published=False)

    deposit.publish()
    edited_deposit = deposit.edit()
    edited_deposit['description'] = 'Another description'
    edited_deposit.update()  # try this
    edited_deposit.publish()

    _, record = edited_deposit.fetch_published()
    assert record['description'] == 'Another description'
