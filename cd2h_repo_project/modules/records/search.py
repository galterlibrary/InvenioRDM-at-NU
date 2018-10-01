"""Configuration for Deposit search."""

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
        return ~Q('term', _deposit__status='draft')


class RecordsSearch(_RecordsSearch):
    """Default search class."""

    class Meta:
        """Configuration for Deposit search."""

        index = 'records'
        doc_types = None
        fields = ('*', )
        facets = {
            'status': TermsFacet(field='_deposit.status'),
        }
        default_filter = DefaultFilter(records_filter)


def deposits_filter():
    """Query ElasticSearch for a filtered list of Deposits.

    Permit the user to see all if:

    * The user is an admin (see
        func:`invenio_deposit.permissions:admin_permission_factory`).

    * It's called outside of a request.

    Otherwise, it filters out any deposit where user is not the owner.
    """
    if (not has_request_context() or
            Permission(ActionNeed('admin-access')).can()):
        return Q()
    else:
        return Q(
            'match', **{'_deposit.owners': getattr(current_user, 'id', 0)}
        )


class DepositsSearch(_RecordsSearch):
    """Default search class."""

    class Meta:
        """Configuration for Deposit search."""

        index = 'records'  # A Deposit is just an unpublished Record
        doc_types = None
        fields = ('*', )
        facets = {
            'status': TermsFacet(field='_deposit.status'),
        }
        default_filter = DefaultFilter(deposits_filter)
