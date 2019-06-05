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
def create_loaded_record():
    """Factory pattern for a loaded Record.

    The returned dict record is the equivalent of the output of the
    marshmallow loader.

    It provides a default value for each required field.
    """
    def _create_loaded_record(data={}):
        data_to_use = {
            'title': 'A title',
            'authors': [
                {
                    'first_name': 'An',
                    'last_name': 'author',
                    'full_name': 'Author, An'
                }
            ],
            'description': 'A description',
            'resource_type': {
                'general': 'other',
                'specific': 'other',
                'full_hierarchy': ['other', 'other'],
            },
            'license': 'mit-license',
            'permissions': 'all_view',
        }
        data_to_use.update(data)
        return data_to_use

    return _create_loaded_record


@pytest.fixture
def create_record(db, es_clear, locations, create_loaded_record):
    """Factory pattern to create a Record."""
    def _create_record(data={}, published=True):
        data['$schema'] = (
            current_app.extensions['invenio-jsonschemas']
            .path_to_url('records/record-v0.1.0.json')
        )
        _deposit = data.pop('_deposit', {})

        data_to_use = create_loaded_record(data)

        record = Deposit.create(data_to_use)

        # Have to modify `_deposit` content after the record is initially
        # created because `_deposit` is used to choose to mint or not
        if _deposit:
            for key, value in _deposit.items():
                record.model.json['_deposit'][key] = value
            db.session.add(record.model)

        if published:
            record.publish()
            pid, record = record.fetch_published()

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
        provided_str_needs = info.pop('provides', [])
        user_info.update(info)
        datastore = current_app.extensions['security'].datastore
        user = datastore.create_user(**user_info)

        with db.session.begin_nested():
            # Note that db.session.begin_nested() is a shorthand way of
            # flushing before and after the following
            needs = current_app.extensions['invenio-access'].actions
            for str_need in provided_str_needs:
                need = needs.get(str_need, None)
                if need:
                    db.session.add(
                        ActionUsers.create(action=need, user=user)
                    )

        return user

    return _create_user


@pytest.fixture
def super_user(db, create_user):
    """Admin user."""
    return create_user({
        'email': 'admin@example.com',
        'password': 'admin123',
        'provides': ['superuser-access']  # from invenio-access module
    })
