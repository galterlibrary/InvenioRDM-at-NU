# -*- coding: utf-8 -*-
#
# This file is part of menRva.
# Copyright (C) 2018-present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test DataCite serialization."""
import html
import xml.etree.ElementTree as ET
from datetime import date

import pytest
from invenio_pidstore.models import PersistentIdentifier

from cd2h_repo_project.modules.doi.serializers import datacite_v41
from cd2h_repo_project.modules.records.minters import mint_pids_for_record


# TODO: Figure a way to get a module-level fixture from create_record
@pytest.fixture
def datacite_record(create_record):
    record = create_record(
        {
            'authors': [
                {
                    'first_name': 'A',
                    'middle_name': 'first',
                    'last_name': 'Author',
                    'full_name': 'Author, A First',
                },
                {
                    'first_name': 'An',
                    'last_name': 'Author',
                    'full_name': 'Author, An',
                },
            ],
            'resource_type': {
                'general': 'multimedia',
                'specific': 'software/source code',
                'full_hierarchy': ['software', 'software or program code'],
            },
        },
        published=False
    )
    mint_pids_for_record(record.id, record)
    pid = PersistentIdentifier.get('doi', record['id'])
    datacite_record = datacite_v41.serialize(pid, record)
    print(datacite_record)  # Kept for nicer test/debugging experience
    return ET.fromstring(datacite_record)


class TestDataCiteV4(object):
    """Test DataCiteV4 serialization"""

    NAMESPACES = {'default': 'http://datacite.org/schema/kernel-4'}

    def test_serializes_empty_identifier(self, datacite_record):
        identifier = datacite_record.find(
            './default:identifier', self.NAMESPACES
        )
        assert identifier.attrib['identifierType'] == 'DOI'
        assert identifier.text == 'DUMMY'

    def test_serializes_creators(self, datacite_record):
        namespaces = self.NAMESPACES
        creators = datacite_record.findall(
            './default:creators/default:creator', namespaces
        )
        assert len(creators) == 2
        assert (
            creators[0].find('default:creatorName', namespaces).text ==
            'Author, A First'
        )
        assert (
            creators[0].find('default:givenName', namespaces).text == 'A'
        )
        assert (
            creators[0].find('default:familyName', namespaces).text == 'Author'
        )
        assert (
            creators[1].find('default:creatorName', namespaces).text ==
            'Author, An'
        )
        assert (
            creators[1].find('default:givenName', namespaces).text == 'An'
        )
        assert (
            creators[1].find('default:familyName', namespaces).text == 'Author'
        )

    def test_serializes_titles(self, datacite_record):
        titles = datacite_record.findall(
            './default:titles/default:title', self.NAMESPACES
        )
        assert len(titles) == 1
        assert titles[0].text == 'A title'

    def test_serializes_publisher(self, config, datacite_record):
        publisher = datacite_record.find(
            './default:publisher', self.NAMESPACES
        )
        assert publisher.text == config['DOI_PUBLISHER']

    def test_serializes_publicationYear(self, datacite_record):
        publication_year = datacite_record.find(
            './default:publicationYear', self.NAMESPACES
        )
        assert publication_year.text == str(date.today().year)

    def test_serializes_resourceType(self, datacite_record):
        resource_type = datacite_record.find(
            './default:resourceType', self.NAMESPACES
        )
        assert resource_type.attrib['resourceTypeGeneral'] == 'Software'
        assert resource_type.text == 'Software/Source Code'
