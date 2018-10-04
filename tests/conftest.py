# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Common pytest fixtures and plugins."""
import shutil
import tempfile

import pytest
from flask import current_app
from invenio_files_rest.models import Bucket, Location
from invenio_pidstore import current_pidstore
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from cd2h_repo_project.modules.records.api import Deposit


@pytest.fixture
def locations(db):
    """File system locations."""
    data_path = tempfile.mkdtemp()
    archive_path = tempfile.mkdtemp()

    location = Location(name='data', uri=data_path, default=True)
    archive_location = Location(
        name='archive',
        uri=archive_path,
        default=False
    )
    db.session.add(location)
    db.session.add(archive_location)
    db.session.commit()

    yield {'data': data_path, 'archive': archive_path}

    shutil.rmtree(data_path)
    shutil.rmtree(archive_path)


@pytest.fixture
def create_serialized_record():
    """Factory pattern for a serialized Record."""
    def _create_serialized_record(data={}):
        data_to_use = {
            'title': 'A title',
            'author': 'An author',
            'description': 'A description',
            'license': 'mit-license',
        }
        data_to_use.update(data)
        return data_to_use

    return _create_serialized_record


@pytest.fixture
def create_record(db, locations, create_serialized_record):
    """Factory pattern to create a Record."""
    def _create_record(data={}, published=True):
        data['$schema'] = (
            current_app.extensions['invenio-jsonschemas']
            .path_to_url('records/record-v0.1.0.json')
        )
        data_to_use = create_serialized_record(data)

        # A Deposit is an unpublished Record
        record = Deposit.create(data_to_use)

        if published:
            record.publish()

        db.session.commit()
        return record

    return _create_record
