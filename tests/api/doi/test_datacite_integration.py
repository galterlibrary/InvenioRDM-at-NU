# -*- coding: utf-8 -*-
#
# This file is part of menRva.
# Copyright (C) 2018-present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Datacite Integration testing.

Unskip these tests to debug an interface problem with DataCite. Other tests
already check for contract integrity, but this allows us to check if the
contract itself is (still) valid.
"""

from datetime import date

import pytest
from datacite.client import DataCiteMDSClient
from invenio_pidstore.models import PersistentIdentifier

from cd2h_repo_project.modules.doi.serializers import datacite_v41
from cd2h_repo_project.modules.records.minters import mint_pids_for_record


@pytest.mark.skip()
def test_client_metadata_post(app, config, create_record):
    """Test posting metadata to DataCite."""
    client = DataCiteMDSClient(
        username=config['PIDSTORE_DATACITE_USERNAME'],
        password=config['PIDSTORE_DATACITE_PASSWORD'],
        prefix=config['PIDSTORE_DATACITE_DOI_PREFIX'],
        test_mode=config['PIDSTORE_DATACITE_TESTMODE'],
        url=config['PIDSTORE_DATACITE_URL']
    )

    record = create_record(
        {
            'title': 'Test-{}'.format(date.today()),
            'authors': [
                {
                    'first_name': 'John',
                    'last_name': 'Smith',
                    'full_name': 'Smith, John'
                }
            ],
            'resource_type': {
                'general': 'images',
                'specific': 'photograph',
                'full_hierarchy': ['image', 'still image', 'photograph'],
            }
        },
        published=False
    )
    mint_pids_for_record(record.id, record)
    doi_pid = PersistentIdentifier.get(pid_type='doi', pid_value=record['id'])
    serialized_record = datacite_v41.serialize(doi_pid, record)

    result = client.metadata_post(serialized_record)

    assert result
