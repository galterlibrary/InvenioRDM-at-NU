"""DOI serializer for external service."""

from invenio_records_rest.serializers.datacite import DataCite41Serializer

from .schemas import DataCiteSchemaV4

# Datacite format serializer
datacite_v41 = DataCite41Serializer(DataCiteSchemaV4, replace_refs=True)
