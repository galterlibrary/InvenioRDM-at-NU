# -*- coding: utf-8 -*-

"""Record serializers."""

from invenio_records_rest.serializers.response import (
    record_responsify, search_responsify
)

from ..marshmallow import RecordSchemaV1
from .json import MenRvaJSONSerializer

# Serializers
# ===========
#: JSON serializer definition.
json_v1 = MenRvaJSONSerializer(RecordSchemaV1, replace_refs=True)

# Records-REST serializers
# ========================
#: JSON record serializer for individual records.
json_v1_response = record_responsify(json_v1, 'application/json')
#: JSON record serializer for search results.
json_v1_search = search_responsify(json_v1, 'application/json')

__all__ = (
    'json_v1',
    'json_v1_response',
    'json_v1_search',
)
