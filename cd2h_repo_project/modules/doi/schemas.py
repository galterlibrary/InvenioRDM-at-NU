"""JSON Schemas."""
from datetime import date

from flask import current_app
from marshmallow import Schema, fields


class DataCiteResourceTypeSchemaV4(Schema):
    """ResourceType schema."""

    resourceTypeGeneral = fields.Method('get_general_resource_type')
    resourceType = fields.Method('get_specific_resource_type')

    def get_general_resource_type(self, resource_type):
        """Extract general_resource_type.

        TODO: Settle on general resource types and use those.
        We just provide a default for now.
        """
        return resource_type.get('general', 'Dataset')

    def get_specific_resource_type(self, resource_type):
        """Extract specific resource type.

        TODO: Settle on specific resource types (if any) and use those.
        We just provide a default for now.
        """
        return resource_type.get('specific', 'Dataset')


class DataCiteTitleSchemaV4(Schema):
    """Title schema."""

    title = fields.Str()


class DataCiteCreatorSchemaV4(Schema):
    """Creator schema."""

    # Note: Marshmallow doesn't try to automatically extract a field
    #       corresponding to a fields.Method.
    creatorName = fields.Method('get_creator_name')
    # TODO optional:
    # givenName
    # familyName

    def get_creator_name(self, author):
        """Extract creator name."""
        name_parts = author.strip().split()
        if len(name_parts) >= 2:
            return "{last_name}, {first_name}".format(
                last_name=name_parts[-1], first_name=name_parts[0])
        else:
            return ''


class DataCiteSchemaV4(Schema):
    """Schema for DataCite Metadata.

    For now, only the minimum required fields are implemented. In the future,
    we may want to include optional fields as well.

    Fields and subfields are based on
    schema.datacite.org/meta/kernel-4.1/doc/DataCite-MetadataKernel_v4.1.pdf
    """

    identifier = fields.Method(
        'get_identifier',
        attribute='metadata.doi',
        dump_only=True)
    creators = fields.List(
        fields.Nested(DataCiteCreatorSchemaV4),
        attribute='metadata.author',
        dump_only=True)
    titles = fields.List(
        fields.Nested(DataCiteTitleSchemaV4),
        attribute='metadata',
        dump_only=True)
    publisher = fields.Method('get_publisher', dump_only=True)
    publicationYear = fields.Method('get_year', dump_only=True)
    resourceType = fields.Nested(
        DataCiteResourceTypeSchemaV4,
        attribute='metadata',  # TODO: 'metadata.resource_type' when added
        dump_only=True)

    def get_identifier(self, obj):
        """Get record main identifier."""
        return {
            'identifier': obj['metadata'].get('doi', ''),
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