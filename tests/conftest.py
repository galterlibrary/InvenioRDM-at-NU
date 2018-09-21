# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Common pytest fixtures and plugins."""

import pytest
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record


# TODO: Would factory_boy simplify our life?
@pytest.fixture
def record():
    """Record fixture."""
    record = Record.create({
        'title': 'A record',
        'author': 'An author',
        'description': 'A description'
    })
    pid = PersistentIdentifier.create(
        pid_type='recid', pid_value=1, object_type='rec',
        object_uuid=record.id, status=PIDStatus.REGISTERED
    )
    return record
