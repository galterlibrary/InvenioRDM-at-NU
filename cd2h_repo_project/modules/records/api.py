"""CD2H's version of a deposit."""

from flask import current_app
from invenio_deposit.api import Deposit as _Deposit
from invenio_files_rest.models import Bucket
from invenio_records_files.models import RecordsBuckets


class Deposit(_Deposit):
    """CD2H's version of a deposit.

    Needed in order to create a bucket and fill
    the `'_buckets'` field to have have an associated url.

    Sorry about the inheritance tree, Invenio started it!
    """

    @classmethod
    def create(cls, data, id_=None):
        """Generate a Deposit object."""
        # TODO: Configure quota_size and max_file_size
        bucket = Bucket.create(
            storage_class=current_app.config['DEPOSIT_DEFAULT_STORAGE_CLASS']
        )
        data['_buckets'] = {'deposit': str(bucket.id)}
        deposit = super(Deposit, cls).create(data, id_=id_)
        RecordsBuckets.create(record=deposit.model, bucket=bucket)
        return deposit
