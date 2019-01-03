# -*- coding: utf-8 -*-

"""JSON Schemas."""

from __future__ import absolute_import, print_function

from collections import namedtuple

from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import DateString, SanitizedUnicode
from invenio_rest.errors import RESTValidationError
from marshmallow import Schema, fields, missing, post_load, validate

from cd2h_repo_project.modules.records.api import RecordType

License = namedtuple('License', ['name', 'value'])
# WARNING: Any change to this list should be reflected in deposit_form.json
LICENSES = [
    License(name="MIT License", value="mit-license"),
    License(name="Creative Commons Attribution", value="cc-by"),
    License(name="Creative Commons Attribution Share-Alike",
            value="cc-by-sa"),
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

    id = fields.Function(serialize=get_id, deserialize=get_id)
    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    description = SanitizedUnicode(
        required=True, validate=validate.Length(min=3)
    )
    author = SanitizedUnicode(required=True, validate=validate.Length(min=3))
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


class RecordSchemaV1(StrictKeysMixin):
    """Record schema.

    Note: When it comes to dumping, any data from the dumper that is not
          accounted for by this, will not be present in the dump.
    """

    id = fields.Function(serialize=get_id, deserialize=get_id)
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
        data['$schema'] = (
            'https://cd2hrepo.galter.northwestern.edu/'
            'schemas/records/record-v0.1.0.json'
        )

        return data
