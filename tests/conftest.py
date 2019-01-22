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
from invenio_access.models import ActionUsers
from invenio_access.permissions import superuser_access
from invenio_files_rest.models import Bucket, Location
from invenio_pidstore import current_pidstore
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_search import current_search

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
def create_record(db, es_clear, locations, create_serialized_record):
    """Factory pattern to create a Record."""
    def _create_record(data={}, published=True):
        data['$schema'] = (
            current_app.extensions['invenio-jsonschemas']
            .path_to_url('records/record-v0.1.0.json')
        )
        _deposit = data.pop('_deposit', {})

        data_to_use = create_serialized_record(data)

        record = Deposit.create(data_to_use)

        # Have to modify `_deposit` content after the record is initially
        # created because `_deposit` is used to choose to mint or not
        if _deposit:
            for key, value in _deposit.items():
                record.model.json['_deposit'][key] = value
            db.session.add(record.model)

        if published:
            record = record.publish()

        # Flush to index and database
        current_search.flush_and_refresh(index='*')
        db.session.commit()

        return record

    return _create_record


@pytest.fixture
def create_user(db):
    """Create a user."""
    def _create_user(info={}):
        default_data = {'email': 'info@inveniosoftware.org',
                        'password': 'tester', 'active': True}
        user_info = default_data.copy()
        is_super_user = info.pop('super', False)
        user_info.update(info)
        datastore = current_app.extensions['security'].datastore
        user = datastore.create_user(**user_info)

        with db.session.begin_nested():
            # Note that db.session.begin_nested() is a shorthand way of
            # committing before and after the following
            if is_super_user:
                db.session.add(
                    ActionUsers.create(action=superuser_access, user=user)
                )

        return user

    return _create_user


@pytest.fixture
def super_user(db, create_user):
    """Admin user."""
    return create_user({
        'email': 'admin@example.com',
        'password': 'admin123',
        'super': True
    })
