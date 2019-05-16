# -*- coding: utf-8 -*-
#
# This file is part of menRva.
# Copyright (C) 2018-present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""menRva JSON serializer."""
from copy import deepcopy

from flask import json
from invenio_records_rest.serializers.json import JSONSerializer


class MenRvaJSONSerializer(JSONSerializer):
    """Custom JSON serializer.

    Used to modify the search aggregation results for now.
    """

    def transform_aggregation(self, aggregation):
        """Conform 'subjects' aggregation to frontend format."""
        if not aggregation or 'subjects' not in aggregation:
            return aggregation

        aggregation = deepcopy(aggregation)

        def buckets(container):
            """Generate output buckets from container with 'buckets' key."""
            in_buckets = container.get('buckets', [])
            out_buckets = []

            for in_bucket in in_buckets:
                out_bucket = {
                    'doc_count': in_bucket['record_count']['doc_count'],
                    'key': in_bucket['key']
                }

                # Potential TODO: allow 'value' to be arbitrary since we only
                #                 care about inner presence of 'buckets'
                sub_category = 'subject'
                sub_container = in_bucket.get(sub_category, {})
                if sub_container:
                    out_bucket[sub_category] = {
                        'buckets': buckets(sub_container),
                        'doc_count_error_upper_bound': (
                            sub_container.get('doc_count_error_upper_bound', 0)
                        ),
                        'sum_other_doc_count': (
                            sub_container.get('sum_other_doc_count', 0)
                        )
                    }

                out_buckets.append(out_bucket)

            return out_buckets

        source = aggregation['subjects'].get('source', {})
        aggregation['subjects'] = {
            "buckets": buckets(source),
            "doc_count_error_upper_bound": (
                source.get('doc_count_error_upper_bound', 0)
            ),
            "sum_other_doc_count": source.get('sum_other_doc_count', 0)
        }

        return aggregation

    def serialize_search(self, pid_fetcher, search_result, links=None,
                         item_links_factory=None, **kwargs):
        """Serialize a search result.

        Overrides parent's serialize_search. This is done to format
        the 'subjects' aggregation per what the frontend expects.

        :param pid_fetcher: Persistent identifier fetcher.
        :param search_result: Elasticsearch search result.
        :param links: Dictionary of links to add to response.
        :param item_links_factory: Factory to create links to add to response.
        """
        hits_dict = {
            'hits': {
                'hits': [
                    self.transform_search_hit(
                        pid_fetcher(hit['_id'], hit['_source']),
                        hit,
                        links_factory=item_links_factory,
                        **kwargs
                    )
                    for hit in search_result['hits']['hits']
                ],
                'total': search_result['hits']['total']
            },
            'links': links or {},
            # This is the only new/different thing from parent
            'aggregations': self.transform_aggregation(
                search_result.get('aggregations', {})
            )
        }

        return json.dumps(hits_dict, **self._format_args())
