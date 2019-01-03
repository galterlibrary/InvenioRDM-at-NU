"""Configuration for Deposit search.

NOTE: In all search cases, the output from the index is serialized into JSON
      as defined by json_v1_search in modules.records.serializers.
"""

from elasticsearch_dsl import Q, TermsFacet
from flask import has_request_context
from flask_login import current_user
from flask_principal import ActionNeed
from invenio_access import Permission
from invenio_search import RecordsSearch as _RecordsSearch
from invenio_search.api import DefaultFilter


def records_filter():
    """Query ElasticSearch for a filtered list of Records.

    Permit the user to see all if:

    * The user is an admin.

    * It's called outside of a request.

    Otherwise, it filters out any Record that has a draft status.
    """
    if (not has_request_context() or
            Permission(ActionNeed('admin-access')).can()):
        return Q()
    else:
        return Q('match', type='published')


class RecordsSearch(_RecordsSearch):
    """Default Record search class."""

    class Meta:
        """Configuration for Deposit search."""

        index = 'records'
        doc_types = None
        fields = ('*', )
        facets = {
            'status': TermsFacet(field='_deposit.status'),
        }
        default_filter = DefaultFilter(records_filter)


def owned_deposits_filter():
    """Query ElasticSearch for a filtered list of owned Deposits.

    It returns:
    - published records
    - unpublished draft records (doesn't return published draft records)

    It sssumes its running inside a request context.
    """
    # TODO: consider other cases like records_filter
    return (
        Q('match', **{'_deposit.owners': getattr(current_user, 'id', 0)}) &
        (Q('match', **{'type': 'published'}) |
         (Q('match', type='draft') & Q('match', _deposit__status='draft')))
    )


class DepositsSearch(_RecordsSearch):
    """Default Deposit search class."""

    class Meta:
        """Configuration for Deposit search."""

        index = 'records'  # Drafts and Published Records are indexed there
        doc_types = None
        fields = ('*', )
        facets = {
            'status': TermsFacet(field='_deposit.status'),
        }
        default_filter = DefaultFilter(owned_deposits_filter)
