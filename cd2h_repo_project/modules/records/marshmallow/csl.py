# -*- coding: utf-8 -*-
#
# This file is part of menRva.
# Copyright (C) 2018-present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Citation Style Language (CSL) Schemas."""

import csv
import re
from datetime import date
from os.path import dirname, join, realpath

from flask import current_app
from invenio_formatter.filters.datetime import from_isodate
from invenio_records_rest.schemas.fields import DateString, SanitizedUnicode
from marshmallow import (
    Schema, ValidationError, fields, missing, post_load, pre_load, validate,
    validates_schema
)

from cd2h_repo_project.modules.records.resource_type import ResourceType


class CSLResourceTypeMap(object):
    """CSL Resource Type Mapping.

    TODO: If we reuse this Mapping pattern again, abstract away.
    """

    def __init__(self):
        """Constructor."""
        self.filename = join(
            dirname(dirname(realpath(__file__))),
            'data', 'resource_type_mapping.csv'
        )
        with open(self.filename) as f:
            reader = csv.DictReader(f)
            self.map = {
                (
                    row['Group'].lower(),
                    row['Name'].lower()
                ):
                row['CSL'].strip()
                for row in reader
            }

    def get(self, key, default=None):
        """Return the mapped value.

        `key` is (<general resource type>, <specific resource type>).
        """
        return self.map.get(key, default)


class CSLAuthorSchemaV1(Schema):
    """Schema for an author."""

    family = SanitizedUnicode(attribute='last_name')
    given = SanitizedUnicode(attribute='first_name')


class CSLRecordSchemaV1(Schema):
    """Schema for records in CSL-JSON.

    The data passed to this schema is a preprocessed record:

        dict(
            pid=<PersistentIdentifier>,
            metadata=<Record dict>,
            links=<links_factory result>,
            revision=<Record revision_id>,
            created=<iso formatted creation date_time string>,
            updated=<iso formatted last updated date_time string>
        )
    """

    id = fields.Str(attribute='pid.pid_value')
    type = fields.Method('get_resource_type')
    title = SanitizedUnicode(attribute='metadata.title')
    author = fields.List(
        fields.Nested(CSLAuthorSchemaV1),
        attribute='metadata.authors'
    )
    issued = fields.Method('get_issue_date')
    DOI = fields.Str(attribute='metadata.doi')
    publisher = fields.Method('get_publisher')

    # TODO: Enable when appropriate metadata exists
    # abstract = fields.Str(attribute='metadata.description')
    # language = fields.Str(attribute='metadata.language')
    # version = fields.Str(attribute='metadata.version')
    # note = fields.Str(attribute='metadata.notes')
    # ISBN = fields.Str(attribute='metadata.imprint.isbn')
    # ISSN = fields.Method('get_issn')
    # container_title = fields.Method('get_container_title')
    # page = fields.Method('get_pages')
    # volume = fields.Str(attribute='metadata.journal.volume')
    # issue = fields.Str(attribute='metadata.journal.issue')
    # publisher_place = fields.Str(attribute='metadata.imprint.place')

    def get_resource_type(self, data):
        """Get CSL resource type.

        The CSL resource type is from a controlled vocabulary that maps to our
        general_resource_type.
        """
        metadata = data['metadata']
        resource_type_obj = ResourceType.get(
            metadata['resource_type']['general'],
            metadata['resource_type']['specific']
        )
        return resource_type_obj.map(CSLResourceTypeMap()) or 'article'

    def get_publisher(self, data):
        """Get publisher."""
        return current_app.config['DOI_PUBLISHER']

    def get_issue_date(self, data):
        """Get a date in list format."""
        d = from_isodate(data['created'])
        return {'date-parts': [[d.year, d.month, d.day]]}

    # TODO: Enable when appropriate metadata exists
    # def get_journal_or_part_of(self, obj, key):
    #     """Get journal or part of."""
    #     m = obj['metadata']
    #     journal = m.get('journal', {}).get(key)
    #     part_of = m.get('part_of', {}).get(key)
    #     return journal or part_of or missing

    # TODO: Enable when appropriate metadata exists
    # def get_container_title(self, obj):
    #     Get container title.
    #     return self.get_journal_or_part_of(obj, 'title')

    # TODO: Enable when appropriate metadata exists
    # def get_pages(self, obj):
    #     """Get pages."""
    #     # Remove multiple dashes between page numbers (eg. 12--15)
    #     pages = self.get_journal_or_part_of(obj, 'pages')
    #     pages = re.sub('-+', '-', pages) if pages else pages
    #     return pages

    # TODO: Enable when appropriate metadata exists
    # def get_issn(self, obj):
    #     """Get the record's ISSN."""
    #     for id in obj['metadata'].get('alternate_identifiers', []):
    #         if id['scheme'] == 'issn':
    #             return id['identifier']
    #     return missing
