from invenio_files_rest.models import Bucket
from invenio_records.models import RecordMetadata
from invenio_records_files.models import RecordsBuckets

from cd2h_repo_project.modules.records.api import Deposit, RecordType


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


def test_deposit_publish(locations):
    deposit = Deposit.create({})

    deposit_record = deposit.publish()
    pid, published_record = deposit_record.fetch_published()

    assert deposit_record['type'] == RecordType.draft.value
    assert published_record['type'] == RecordType.published.value


def test_deposit_edit(create_record):
    deposit = create_record(published=False)
    deposit.publish()  # to set deposit's _deposit.status = 'published'

    draft_record = deposit.edit()

    assert draft_record['type'] == RecordType.draft.value


def test_fetch_deposit(create_record):
    unpublished_record = create_record(published=False)
    unpublished_record.publish()
    _, published_record = unpublished_record.fetch_published()

    _, deposit = Deposit.fetch_deposit(published_record)

    assert unpublished_record == deposit


def test_clear_deposit_preserves_appropriate_fields(create_record):
    record = create_record()
    _, deposit = Deposit.fetch_deposit(record)
    fields_to_preserve = ['_buckets', '_deposit', 'id', 'type']
    preserved = {}

    assert deposit['$schema']  # Example of field not to preserve
    for field in fields_to_preserve:
        assert deposit[field]
        preserved[field] = deposit[field]

    deposit['_deposit']['status'] = 'draft'  # Needed to clear
    cleared_deposit = deposit.clear()

    assert '$schema' not in deposit
    for field in fields_to_preserve:
        assert preserved[field] == deposit[field]
