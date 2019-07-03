# -*- coding: utf-8 -*-
#
# This file is part of menRva.
# Copyright (C) 2018-present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test signal hooks."""

from io import BytesIO

from invenio_files_rest.models import Bucket, ObjectVersion
from invenio_indexer.api import RecordIndexer


def test_before_deposit_index_hook_sets_files(create_record, db, es):
    deposit = create_record(published=False)
    # Reproduce file upload: add file to bucket associated with deposit
    bucket = Bucket.get(deposit['_buckets']['deposit'])
    obj = ObjectVersion.create(bucket, 'foo.txt')
    stream = BytesIO(b'Hello world!')
    obj.set_contents(
        stream, size=len(stream.getvalue()), size_limit=bucket.size_limit
    )
    db.session.commit()
    indexer = RecordIndexer()

    indexer.index(deposit)

    # Get the raw indexed document
    index, doc_type = indexer.record_to_index(deposit)
    es_deposit = es.get(index=index, doc_type=doc_type, id=deposit.id)
    assert '_files' in es_deposit['_source']
    assert es_deposit['_source']['_files'][0]['type'] == 'txt'
