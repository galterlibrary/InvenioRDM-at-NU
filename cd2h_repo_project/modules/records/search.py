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

from cd2h_repo_project.modules.records.permissions import RecordPermissions


def nested_filter(path, field):
    """Create a nested filter.

    :param field: Field name.
    :returns: Function that returns the Nested query.
    """
    def inner(values):
        return Q(
            'nested',
            **{
                'path': path,
                'query': Q('terms', **{field: values})
            }
        )

    return inner


def records_filter():
    """Query ElasticSearch for a *filtered* list of Records.

    NOTE: Any of these queries is run in a filtered context. So ES can
          optimize them.
    """
    if not has_request_context():
        return Q()
    elif Permission(ActionNeed('admin-access')).can():
        return Q()
    elif not current_user.is_authenticated:
        return (
            Q('term', type='published') &
            Q('term', permissions=RecordPermissions.ALL_VIEW)
        )
    else:
        return (
            Q('term', type='published') &
            (
                Q('term', permissions=RecordPermissions.ALL_VIEW) |
                Q('term', permissions=RecordPermissions.RESTRICTED_VIEW) |
                (
                    Q('term', permissions=RecordPermissions.PRIVATE_VIEW) &
                    Q('term', _deposit__owners=getattr(current_user, 'id', 0))
                )
            )
        )


class RecordsSearch(_RecordsSearch):
    """Main Record search class."""

    class Meta:
        """Configuration for Records search."""

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
