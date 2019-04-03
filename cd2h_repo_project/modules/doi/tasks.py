"""CD2H Celery tasks."""
import re

from celery import shared_task
from datacite.client import DataCiteMDSClient
from datacite.errors import DataCiteError, HttpError
from elasticsearch.exceptions import RequestError
from flask import current_app
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier

from cd2h_repo_project.modules.doi.serializers import datacite_v41
from cd2h_repo_project.modules.records.api import Deposit
from cd2h_repo_project.modules.records.links import (
    url_for_record_ui_recid_external
)
from cd2h_repo_project.modules.records.resolvers import record_resolver


def extract_doi(status_str):
    """Extract minted DOI from response.

    Exceptions percolate.
    """
    return re.search("\(([-.a-zA-Z0-9\/]+)\)$", status_str).group(1)


@shared_task(ignore_result=True, max_retries=6, default_retry_delay=10 * 60,
             rate_limit='100/m')
def register_doi(recid_pid_value):
    """External DOI registration task.

    This asynchronous task mints a DOI with the external service and
    stores it in the local doi PID. It will retry a `max_retries` number of
    times.

    `default_retry_delay` is in seconds.

    :param recid_pid_value: pid_value of recid-PID for the target record.
                            Note that this pid_value is also the pid_value of
                            the doi-PID associated with the target record if
                            it has not been DOI-minted yet.
    """
    try:
        recid_pid, record = record_resolver.resolve(str(recid_pid_value))
        depid_pid, deposit = Deposit.fetch_deposit(record)

        doi_pid_value = record.get('doi') or recid_pid_value
        doi_pid = PersistentIdentifier.get(
            pid_type='doi', pid_value=doi_pid_value)

        client = DataCiteMDSClient(
            username=current_app.config['PIDSTORE_DATACITE_USERNAME'],
            password=current_app.config['PIDSTORE_DATACITE_PASSWORD'],
            prefix=current_app.config['PIDSTORE_DATACITE_DOI_PREFIX'],
            test_mode=current_app.config['PIDSTORE_DATACITE_TESTMODE'],
            url=current_app.config['PIDSTORE_DATACITE_URL']
        )

        # Mint DOI
        serialized_record = datacite_v41.serialize(doi_pid, record)
        result = client.metadata_post(serialized_record)

        # When minting for the first time, we need to associate the
        # record's page to its metadata record on Datacite
        if doi_pid.is_new():
            minted_doi = extract_doi(result)
            landing_url = url_for_record_ui_recid_external(recid_pid_value)
            client.doi_post(minted_doi, landing_url)

            # Update doi_pid
            doi_pid.pid_value = minted_doi
            doi_pid.register()

            # Update deposit/record
            deposit['doi'] = minted_doi
            record['doi'] = minted_doi
            deposit.commit()
            record.commit()
            # The above only flushes (no db commit). The below is needed to
            # persist the changes to the db.
            db.session.commit()

            # Re-index deposit/record
            RecordIndexer().index(deposit)
            RecordIndexer().index(record)

    except (HttpError, DataCiteError) as e:
        register_doi.retry(exc=e)
    except RequestError:
        current_app.logger.exception('Could not index {}.'.format(record))
    except Exception as e:
        current_app.logger.exception(
            'Exception in register_doi for recid_pid_value: {}. Retrying...'
            .format(recid_pid_value))
        register_doi.retry(exc=e)
