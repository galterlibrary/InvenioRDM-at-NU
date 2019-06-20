"""JSON Schemas."""
import csv
from collections import defaultdict
from datetime import date
from os.path import dirname, join, realpath

from flask import current_app
from marshmallow import Schema, fields

from cd2h_repo_project.modules.records.resource_type import ResourceType


class DataCiteResourceTypeMap(object):
    """DataCite Resource Type Mapping.

    TODO: If we extract this module out, make this class a configuration
          setting.
    """

    def __init__(self):
        """Constructor."""
        self.filename = join(
            dirname(dirname(realpath(__file__))),
            'records', 'data', 'resource_type_mapping.csv'
        )
        with open(self.filename) as f:
            reader = csv.DictReader(f)
            self.map = {
                (row['Group'].lower(), row['Name'].lower()):
                row['DataCite'].strip()
                for row in reader
            }

    def get(self, key, default=None):
        """Return the mapped value.

        `key` is (<general resource type>, <specific resource type>).
        """
        return self.map.get(key, default)


class DataCiteResourceTypeSchemaV4(Schema):
    """ResourceType schema."""

    resourceTypeGeneral = fields.Method('get_general_resource_type')
    resourceType = fields.Method('get_specific_resource_type')

    def get_general_resource_type(self, resource_type):
        """Return DataCite's controlled vocabulary General Resource Type."""
        resource_type_obj = ResourceType.get(
            resource_type['general'], resource_type['specific']
        )
        return resource_type_obj.map(DataCiteResourceTypeMap())

    def get_specific_resource_type(self, resource_type):
        """Return title-ized Specific Resource Type."""
        return resource_type['specific'].title()


class DataCiteTitleSchemaV4(Schema):
    """Title schema."""

    title = fields.Str()


class DataCiteCreatorSchemaV4(Schema):
    """Creator schema.

    Each of these fields are inside the `creator` node.
    """

    creatorName = fields.Str(attribute='full_name')
    # TODO (optional): sub creatorName: nameType
    givenName = fields.Str(attribute='first_name')
    familyName = fields.Str(attribute='last_name')
    # TODO (optional):
    # nameIdentifier
    #   nameIdentifierScheme
    #   schemeURI
    # affiliation


class DataCiteSchemaV4(Schema):
    """Schema for DataCite Metadata.

    For now, only the minimum required fields are implemented. In the future,
    we may want to include optional fields as well.

    Fields and subfields are based on
    schema.datacite.org/meta/kernel-4.1/doc/DataCite-MetadataKernel_v4.1.pdf
    """

    identifier = fields.Method('get_identifier', dump_only=True)
    # NOTE: This auto-magically serializes the `creators` and `creator` nodes.
    creators = fields.List(
        fields.Nested(DataCiteCreatorSchemaV4),
        attribute='metadata.authors',
        dump_only=True)
    titles = fields.List(
        fields.Nested(DataCiteTitleSchemaV4),
        attribute='metadata',
        dump_only=True)
    publisher = fields.Method('get_publisher', dump_only=True)
    publicationYear = fields.Method('get_year', dump_only=True)
    resourceType = fields.Nested(
        DataCiteResourceTypeSchemaV4,
        attribute='metadata.resource_type',
        dump_only=True)

    def get_identifier(self, data):
        """Get record main identifier."""
        return {
            # If no DOI, 'DUMMY' value is used and will be ignored by DataCite
            'identifier': data.get('metadata', {}).get('doi') or 'DUMMY',
            'identifierType': 'DOI'
        }

    def get_publisher(self, data):
        """Extract publisher."""
        return current_app.config['DOI_PUBLISHER']

    def get_year(self, data):
        """Extract year.

        Current year for now.
        TODO: Revisit when dealing with embargo.
        """
        return date.today().year
