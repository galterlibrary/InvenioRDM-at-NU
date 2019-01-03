from unittest import TestCase

from invenio_files_rest.models import Bucket
from invenio_records.models import RecordMetadata
from invenio_records_files.models import RecordsBuckets

from cd2h_repo_project.modules.records.api import Deposit


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
    data = {}
    deposit = Deposit.create(data)

    published_record = deposit.publish()

    assert published_record['type'] == 'published'


def test_deposit_edit(create_record, db):
    deposit = create_record()

    draft_record = deposit.edit()

    assert draft_record['type'] == 'draft'
