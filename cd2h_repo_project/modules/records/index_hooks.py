# -*- coding: utf-8 -*-
#
# This file is part of menRva.
# Copyright (C) 2018-present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Indexing signal hooks."""

from invenio_files_rest.models import Bucket
from invenio_records_files.api import FilesIterator


def before_deposit_index_hook(
        sender, json=None, record=None, index=None, **kwargs):
    """Hook to transform Deposits before indexing in ES.

    :param sender: The entity sending the signal.
    :param json: The dumped record dictionary which can be modified.
    :param record: The record (deposit) being indexed.
    :param index: The index in which the record will be indexed.
    :param kwargs: Any other parameters.
    """
    if (index.startswith('records-record') and json.get('type') == 'draft'):
        bucket = Bucket.get(json.get('_buckets', {}).get('deposit'))
        if bucket:
            iterator = FilesIterator(
                record, bucket=bucket, file_cls=record.file_cls
            )
            json['_files'] = iterator.dumps()
