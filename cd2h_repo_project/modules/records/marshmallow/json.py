# -*- coding: utf-8 -*-

"""JSON Schemas.

Here is the Loading/Validating/Dumping order as taken from
https://marshmallow.readthedocs.io/en/2.x-line/extending.html
#pre-post-processor-invocation-order

    1- @pre_load(pass_many=True) methods
    2- @pre_load(pass_many=False) methods
    3- load(in_data, many) (validation and deserialization)
    4- @post_load(pass_many=True) methods
    5- @post_load(pass_many=False) methods

The pipeline for serialization is similar, except that the “pass_many”
processors are invoked after the “non-raw” processors.

    1- @pre_dump(pass_many=False) methods
    2- @pre_dump(pass_many=True) methods
    3- dump(obj, many) (serialization)
    4- @post_dump(pass_many=False) methods
    5- @post_dump(pass_many=True) methods
"""

from __future__ import absolute_import, print_function

from collections import namedtuple

from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import DateString, SanitizedUnicode
from invenio_rest.errors import RESTValidationError
from marshmallow import (
    Schema, ValidationError, fields, missing, post_load, pre_load, validate,
    validates_schema
)

from cd2h_repo_project.modules.records.api import RecordType
from cd2h_repo_project.modules.records.permissions import RecordPermissions
from cd2h_repo_project.modules.records.resource_type import (
    ResourceType, ResourceTypeHierarchy
)
from cd2h_repo_project.modules.records.utilities import to_full_name

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
    full_name = SanitizedUnicode()
    # TODO: ORCID, or even better, nesting of Author PIDs

    @post_load
    def load_full_name(self, data):
        """Load full_name from first, middle and last name.

        Even if full_name is passed, it is overridden because full_name should
        be a constructed internal field. UI doesn't allow manipulation
        of full_name directly.
        """
        data['full_name'] = to_full_name(data)


class TermSchemaV1(StrictKeysMixin):
    """Term schema.

    TODO: Be more discerning of the terms we accept.
    """

    source = fields.Str()
    value = fields.Str()


class ResourceTypeSchemaV1(StrictKeysMixin):
    """Resource type schema."""

    general = fields.Str(required=True)
    specific = fields.Str(required=True)
    # dump_only so the value from ElasticSearch is used (dumped) at search time
    full_hierarchy = fields.List(fields.Str(), dump_only=True)

    @pre_load
    def fill_dataset(self, data):
        """Fills specific resource type to `'dataset'` for `'dataset'`."""
        if data.get('general') == 'dataset':
            data['specific'] = data.get('specific', 'dataset')
        return data

    @validates_schema
    def validate_data(self, data):
        """Validate resource type."""
        resource_type = ResourceType.get(
            data.get('general'),
            data.get('specific'),
        )
        if resource_type is None:
            raise ValidationError('Invalid resource type.')

    @post_load
    def fill_full_hierarchy(self, data):
        """Fills menRva hierarchy."""
        resource_type = ResourceType.get(data['general'], data['specific'])

        data['full_hierarchy'] = resource_type.map(ResourceTypeHierarchy())

        return data


class MetadataSchemaV1(Schema):
    """Schema for the record metadata."""

    id = fields.Function(serialize=get_id, deserialize=get_id, dump_only=True)
    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    authors = fields.Nested(AuthorSchemaV1, required=True, many=True)
    description = SanitizedUnicode(
        required=True, validate=validate.Length(min=3)
    )
    resource_type = fields.Nested(ResourceTypeSchemaV1, required=True)
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
