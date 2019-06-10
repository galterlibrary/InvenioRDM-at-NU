from invenio_pidstore.models import PersistentIdentifier

from cd2h_repo_project.modules.records.serializers import json_v1
from cd2h_repo_project.modules.records.serializers.json import (
    MenRvaJSONSerializer
)


class TestJsonV1(object):
    def test_serializes_persistent_identifier(self, create_record):
        record = create_record()
        pid = PersistentIdentifier.get(
            record['_deposit']['pid']['type'],
            record['_deposit']['pid']['value'],
        )

        serialized_record = json_v1.transform_record(pid, record)

        assert serialized_record['id'] == record['_deposit']['pid']['value']

    def test_serializes_dump_onlys(self, create_record):
        record = create_record()
        pid = PersistentIdentifier.get(
            record['_deposit']['pid']['type'],
            record['_deposit']['pid']['value'],
        )

        serialized_record = json_v1.transform_record(pid, record)

        assert 'created' in serialized_record
        assert 'updated' in serialized_record
        assert 'links' in serialized_record

    def test_serializes_metadata(self, create_record):
        record = create_record()
        pid = PersistentIdentifier.get(
            record['_deposit']['pid']['type'],
            record['_deposit']['pid']['value'],
        )

        serialized_record = json_v1.transform_record(pid, record)

        required_keys = ['title', 'description', 'authors', 'license']
        for key in required_keys:
            assert serialized_record['metadata'][key]


class TestMenRvaJSONSerializer(object):
    """Test MenRvaJSONSerializer."""

    def test_restructure_subjects_aggregation(self):
        aggregation_result = {
            # Arbitrary content - just making sure nothing is changed
            'license': {'buckets': [1]},
            # Structure given by ElasticSearch that we want to change
            'subjects': {
                "doc_count": 7,
                "source": {
                    "buckets": [
                        {
                            "doc_count": 2,
                            "key": "FAST",
                            "record_count": {
                                "doc_count": 2
                            },
                            "subject": {
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "Diabantite",
                                        "record_count": {
                                            "doc_count": 1
                                        }
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "Diabetes",
                                        "record_count": {
                                            "doc_count": 1
                                        }
                                    }
                                ],
                                "doc_count_error_upper_bound": 0,
                                "sum_other_doc_count": 0
                            }
                        },
                        {
                            # Number of *'terms'-documents* (hits) with MeSH
                            "doc_count": 5,
                            "key": "MeSH",
                            # Number of *records* (hits) with MeSH
                            "record_count": {
                                "doc_count": 4
                            },
                            "subject": {
                                "buckets": [
                                    {
                                        "doc_count": 3,
                                        "key": "Diabetes Complications",
                                        "record_count": {
                                            "doc_count": 3
                                        }
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "Diabetes Mellitus",
                                        "record_count": {
                                            "doc_count": 1
                                        }
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "Insulin, Regular, Human",
                                        "record_count": {
                                            "doc_count": 1
                                        }
                                    }
                                ],
                                "doc_count_error_upper_bound": 0,
                                "sum_other_doc_count": 0
                            }
                        }
                    ],
                    "doc_count_error_upper_bound": 0,
                    "sum_other_doc_count": 0
                }
            }
        }

        transformed_search_result = (
            MenRvaJSONSerializer().transform_aggregation(aggregation_result)
        )

        assert aggregation_result['license'] == {'buckets': [1]}
        assert (
            transformed_search_result['license'] ==
            aggregation_result['license']
        )
        assert transformed_search_result['subjects'] == {
            "buckets": [
                {
                    "doc_count": 2,
                    "key": "FAST",
                    "subject": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "key": "Diabantite"
                            },
                            {
                                "doc_count": 1,
                                "key": "Diabetes"
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0
                    }
                },
                {
                    "doc_count": 4,
                    "key": "MeSH",
                    "subject": {
                        "buckets": [
                            {
                                "doc_count": 3,
                                "key": "Diabetes Complications"
                            },
                            {
                                "doc_count": 1,
                                "key": "Diabetes Mellitus"
                            },
                            {
                                "doc_count": 1,
                                "key": "Insulin, Regular, Human"
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0
                    },
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0
        }

    def test_restructure_authors_aggregation(self):
        aggregation_result = {
            "authors": {
                "doc_count": 2,
                "full_name": {
                    "buckets": [
                        {
                            "doc_count": 1,
                            "key": "Smith, John"
                        },
                        {
                            "doc_count": 1,
                            "key": "Doe, Jane"
                        }
                    ],
                    "doc_count_error_upper_bound": 0,
                    "sum_other_doc_count": 0
                }
            },
            "file_type": {
                "buckets": [],
                "doc_count_error_upper_bound": 0,
                "sum_other_doc_count": 0
            }
        }

        transformed_search_result = (
            MenRvaJSONSerializer().transform_aggregation(aggregation_result)
        )

        # Check aggregation_result was not modified (in-place)
        assert aggregation_result["file_type"] == {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0
        }
        assert (
            aggregation_result['file_type'] == aggregation_result["file_type"]
        )

        # Check authors section was restructured
        assert transformed_search_result['authors'] == {
            "buckets": [
                {
                    "doc_count": 1,
                    "key": "Smith, John"
                },
                {
                    "doc_count": 1,
                    "key": "Doe, Jane"
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0
        }
