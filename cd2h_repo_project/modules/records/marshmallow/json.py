# -*- coding: utf-8 -*-

"""JSON Schemas."""

from __future__ import absolute_import, print_function

from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import DateString, SanitizedUnicode
from invenio_rest.errors import RESTValidationError
from marshmallow import Schema, fields, missing, post_dump, post_load, validate


def get_id(obj, context):
    """Get record id."""
    pid = context.get('pid')
    return pid.pid_value if pid else missing


class PersonIdsSchemaV1(StrictKeysMixin):
    """Ids schema."""

    source = fields.Str()
    value = fields.Str()


class ContributorSchemaV1(StrictKeysMixin):
    """Contributor schema."""

    ids = fields.Nested(PersonIdsSchemaV1, many=True)
    name = fields.Str(required=True)
    role = fields.Str()
    affiliations = fields.List(fields.Str())
    email = fields.Str()


class MetadataSchemaV1(Schema):
    """Schema for the record metadata."""

    def get_id(self, obj):
        """Get record id."""
        pid = self.context.get('pid')
        return pid.pid_value if pid else missing

    id = fields.Function(serialize=get_id, deserialize=get_id)
    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    description = SanitizedUnicode(
        required=True, validate=validate.Length(min=3)
    )
    author = SanitizedUnicode(required=True, validate=validate.Length(min=3))


class RecordSchemaV1(StrictKeysMixin):
    """Record schema."""

    id = fields.Function(serialize=get_id, deserialize=get_id)
    metadata = fields.Nested(MetadataSchemaV1)
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)
    schema = fields.Str(attribute="$schema")

    @post_load
    def remove_envelope(self, data):
        """Post process data."""
        # Remove envelope
        if 'metadata' in data:
            data = data['metadata']

        # Artificially insert our schema because invenio-deposit wants it.
        data['$schema'] = (
            'https://cd2hrepo.galter.northwestern.edu/'
            'schemas/records/record-v0.1.0.json'
        )
        return data
