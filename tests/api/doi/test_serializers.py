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
from flask import current_app
from invenio_pidstore.models import PersistentIdentifier

from cd2h_repo_project.modules.doi.serializers import datacite_v41
from cd2h_repo_project.modules.records.minters import mint_pids_for_record


# TODO: Figure a way to get a module-level fixture from create_record
@pytest.fixture
def serialized_record(create_record):
    record = create_record(
        {
            'authors': [
                {
                    'first_name': 'A',
                    'middle_name': 'first',
                    'last_name': 'Author',
                },
                {
                    'first_name': 'An',
                    'middle_name': 'other',
                    'last_name': 'Author',
                },
            ]
        },
        published=False
    )
    mint_pids_for_record(record.id, record)
    pid = PersistentIdentifier.get('doi', record['id'])
    datacite_record = datacite_v41.serialize(pid, record)
    print(datacite_record)  # Kept for nicer test/debugging experience
    return datacite_record


class TestDataCiteV4(object):
    """Test DataCiteV4 serialization"""

    def test_serializes_empty_identifier(self, serialized_record):
        # Expect empty identifier so that DataCite generates it
        assert (
            '<identifier identifierType="DOI"></identifier>' in
            serialized_record
        )

    def test_serializes_creators(self, serialized_record):
        namespaces = {'default': 'http://datacite.org/schema/kernel-4'}
        tree = ET.fromstring(serialized_record)
        creators = tree.findall(
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
            'Author, An Other'
        )
        assert (
            creators[1].find('default:givenName', namespaces).text == 'An'
        )
        assert (
            creators[1].find('default:familyName', namespaces).text == 'Author'
        )

    def test_serializes_titles(self, serialized_record):
        assert "<titles>\n" in serialized_record
        assert "<title>A title</title>" in serialized_record
        assert "</titles>\n" in serialized_record

    def test_serializes_publisher(self, serialized_record):
        assert (
            "<publisher>{}</publisher>".format(
                html.escape(current_app.config['DOI_PUBLISHER'])
            )
            in serialized_record
        )

    def test_serializes_publicationYear(self, serialized_record):
        assert (
            "<publicationYear>{}</publicationYear>".format(date.today().year)
            in serialized_record
        )

    def test_serializes_resourceType(self, serialized_record):
        # TODO: Adjust if when we provide resource type as an input field
        assert (
            '<resourceType resourceTypeGeneral="Dataset">Dataset'
            '</resourceType>' in serialized_record
        )
