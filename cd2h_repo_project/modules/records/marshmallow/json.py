# -*- coding: utf-8 -*-

"""JSON Schemas."""

from __future__ import absolute_import, print_function

from collections import namedtuple

from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import DateString, SanitizedUnicode
from invenio_rest.errors import RESTValidationError
from marshmallow import Schema, fields, missing, post_load, pre_load, validate

from cd2h_repo_project.modules.records.api import RecordType
from cd2h_repo_project.modules.records.permissions import RecordPermissions

License = namedtuple('License', ['name', 'value'])
# WARNING: Any change to this list should be reflected in:
# - modules/records/static/json/records/deposit_form.json
# - modules/records/static/js/search/filters.js
LICENSES = [
    License(name="MIT License", value="mit-license"),
    License(name="Creative Commons Attribution", value="cc-by"),
    License(name="Creative Commons Attribution Share-Alike", value="cc-by-sa"),
    License(name="Creative Commons CCZero", value="cc-zero"),
    License(name="Creative Commons Non-Commercial (Any)", value="cc-nc"),
    License(name="GNU General Public License version 3.0 (GPLv3)",
            value="gpl-3.0"),
    License(name="Other (Open)", value="other-open"),
    License(name="Other (Not Open)", value="other-closed"),
]


def get_id(obj, context):
    """Get record id."""
    pid = context.get('pid')
    return pid.pid_value if pid else missing


class AuthorSchemaV1(StrictKeysMixin):
    """Author schema."""

    first_name = SanitizedUnicode(required=True)
    middle_name = SanitizedUnicode()
    last_name = SanitizedUnicode(required=True)
    # TODO: ORCID, or even better, nesting of Author PIDs


class TermSchemaV1(StrictKeysMixin):
    """Term schema."""

    source = fields.Str()
    value = fields.Str()


class MetadataSchemaV1(Schema):
    """Schema for the record metadata."""

    id = fields.Function(serialize=get_id, deserialize=get_id, dump_only=True)
    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    description = SanitizedUnicode(
        required=True, validate=validate.Length(min=3)
    )
    authors = fields.Nested(AuthorSchemaV1, required=True, many=True)
    license = fields.Str(
        required=True,
        validate=validate.OneOf(
            [l.value for l in LICENSES],
            labels=[l.name for l in LICENSES]
        )
    )
    type = fields.Str(
        dump_only=True,
        validate=validate.OneOf([rt.value for rt in RecordType])
    )
    terms = fields.Nested(TermSchemaV1, many=True)
    # TODO: Replace with more complex object
    permissions = fields.Str(
        required=True,
        validate=validate.OneOf(RecordPermissions.get_values())
    )

    @pre_load
    def coalesce_terms(self, data):
        """Preprocess '*_terms' into `terms`."""
        terms = data.get('terms', [])

        if 'mesh_terms' in data:
            terms.extend(data['mesh_terms'])
        if 'fast_terms' in data:
            terms.extend(data['fast_terms'])

        data['terms'] = terms

        return data


class RecordSchemaV1(StrictKeysMixin):
    """Record schema.

    This acts as a bi-directonal form and data transformer.
    It *loads*, validates and transforms data from the external world, to get a
    "cleaned" data dict.
    It *dumps* data from internal system to get a data dict for external
    consumption.

    Note: When it comes to dumping, any data from the dumper that is not
          accounted for by this, will not be present in the dump.
    """

    id = fields.Function(serialize=get_id, deserialize=get_id, dump_only=True)
    metadata = fields.Nested(MetadataSchemaV1)
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)

    @post_load
    def remove_envelope(self, data):
        """Post process data."""
        # Remove envelope
        if 'metadata' in data:
            data = data['metadata']

        # Artificially insert our schema because invenio-deposit wants it.
        # TODO: Replace cd2hrepo... by configuration variable
        data['$schema'] = (
            'https://cd2hrepo.galter.northwestern.edu/'
            'schemas/records/record-v0.1.0.json'
        )

        return data
