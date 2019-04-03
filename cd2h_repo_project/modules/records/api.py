"""CD2H's version of a deposit."""

from enum import Enum
from os.path import splitext

from elasticsearch.exceptions import RequestError
from flask import current_app
from invenio_deposit.api import Deposit as _Deposit
from invenio_deposit.api import has_status, preserve
from invenio_deposit.providers import DepositProvider
from invenio_deposit.utils import mark_as_action
from invenio_files_rest.models import Bucket
from invenio_pidstore.errors import PIDInvalidAction
from invenio_pidstore.resolver import Resolver
from invenio_records_files.api import FileObject as _FileObject
from invenio_records_files.api import Record as _Record
from invenio_records_files.models import RecordsBuckets
from werkzeug.local import LocalProxy

from .signals import menrva_record_published

current_jsonschemas = LocalProxy(
    lambda: current_app.extensions['invenio-jsonschemas']
)


RECORD_OBJECT_TYPE = 'rec'


class FileObject(_FileObject):
    """menrva file object."""

    def _extract_filetype(self, filename):
        """Extract the file extension without the leading '.'.

        If no file type, return 'other'.
        """
        dot_extension = splitext(filename)[1]
        return dot_extension[1:].lower() if dot_extension else 'other'

    def dumps(self):
        """Serialize as a json compatible dict.

        Add file type as key.
        WARNING: This is a stateful function.
        """
        data = super(FileObject, self).dumps()
        data['type'] = self._extract_filetype(data['key'])
        return data


class Record(_Record):
    """menrva Record.

    Needed because we customized the file class.
    """

    file_cls = FileObject


class RecordType(Enum):
    """
    Enumeration of Record types.

    Is using type pattern over inheritance better here? Time will tell.
    """

    draft = "draft"
    published = "published"


class Deposit(_Deposit):
    """CD2H's in memory API interface to a draft record (a deposit in Invenio).

    This is the model for a draft and Record is the model for a published
    record.

    This is an attempt to rely as much as possible on invenio_deposit
    while customizing for our needs.

    Sorry about the inheritance tree, Invenio started it!
    """

    file_cls = FileObject
    published_record_class = Record
    NON_FORM_FIELDS_TO_PRESERVE = (
        '_deposit',
        'type',
        'id',
        '_buckets',
        'doi'
    )

    @classmethod
    def fetch_deposit(cls, record):
        """Return PID and Deposit tuple of corresponding published record."""
        resolver = Resolver(
            pid_type=DepositProvider.pid_type, object_type=RECORD_OBJECT_TYPE,
            getter=cls.get_record
        )
        return resolver.resolve(record['_deposit']['id'])

    @property
    def record_schema(self):
        """Convert deposit/draft schema to a published schema.

        Overrides parent's `record_schema` to forgo weird hierarchy need.

        :returns: The absolute URL to the schema or `None`.
        """
        schema_path = current_jsonschemas.url_to_path(self['$schema'])
        # schema_path is <deposit prefix>/<record file>
        deposit_schema_prefix = (
            current_app.config['DEPOSIT_JSONSCHEMAS_PREFIX']
        )
        record_schema_prefix = (
            current_app.config['RECORD_JSONSCHEMAS_PREFIX']
        )

        if schema_path and schema_path.startswith(deposit_schema_prefix):
            return current_jsonschemas.path_to_url(
                record_schema_prefix + schema_path[len(deposit_schema_prefix):]
            )

    def build_deposit_schema(self, record):
        """Convert record schema to a valid deposit schema.

        Overrides parent's `build_deposit_schema` to forgo weird
        hierarchy need.

        :param record: The record used to build deposit schema.
        :returns: The absolute URL to the schema or `None`.
        """
        schema_path = current_jsonschemas.url_to_path(record['$schema'])
        deposit_schema_prefix = (
            current_app.config['DEPOSIT_JSONSCHEMAS_PREFIX']
        )
        record_schema_prefix = (
            current_app.config['RECORD_JSONSCHEMAS_PREFIX']
        )

        if schema_path and schema_path.startswith(record_schema_prefix):
            return current_jsonschemas.path_to_url(
                deposit_schema_prefix + schema_path[len(record_schema_prefix):]
            )

    @classmethod
    def create(cls, data, id_=None):
        """Generate a Deposit object.

        Overrides parent's `create`.
        """
        # TODO: Configure quota_size and max_file_size
        bucket = Bucket.create(
            storage_class=current_app.config['DEPOSIT_DEFAULT_STORAGE_CLASS']
        )
        data['_buckets'] = {'deposit': str(bucket.id)}
        # any newly created Deposit is a draft
        data['type'] = RecordType.draft.value
        deposit = super(Deposit, cls).create(data, id_=id_)
        RecordsBuckets.create(record=deposit.model, bucket=bucket)
        return deposit

    @preserve(fields=('_deposit', '$schema', 'type'))
    def merge_with_published(self):
        """Merge changes with latest published version.

        Overrides parent's `merge_with_published` just to preserve `type`.
        """
        return super(Deposit, self).merge_with_published()

    @has_status
    @mark_as_action
    def publish(self, pid=None, id_=None):
        """Publish a deposit.

        Overrides parent's `publish`.
        This is a needed wholesale port with tweaks because the tweaks have
        to be at specific locations.

        If it's the first time the deposit is published:

        * it calls the minter and set the following meta information inside
            the deposit:

        .. code-block:: python

            deposit['_deposit']['pid'] = {
                'type': pid_type,
                'value': pid_value,
                'revision_id': 0,
            }

        * A dump of all information inside the deposit is done.

        * A snapshot of the files is done.

        Otherwise, it publishes the new edited version.
        In this case, if meanwhile someone already published a new
        version, it'll try to merge the changes with the latest version.

        .. note:: no need for indexing as it calls `self.commit()`.

        Status required: ``'draft'``.

        :param pid: Force the new pid value. (Default: ``None``)
        :param id_: Force the new uuid value as deposit id. (Default: ``None``)
        :returns: Returns itself because this is what Invenio Deposit expects.
        """
        pid = pid or self.pid

        if not pid.is_registered():
            raise PIDInvalidAction()

        self['_deposit']['status'] = 'published'

        if self['_deposit'].get('pid') is None:
            published_record = self._publish_new(id_=id_)
        else:  # Publish after edit
            published_record = self._publish_edited()

        published_record['type'] = RecordType.published.value

        published_record.commit()
        self.commit()

        # TODO: Remove? because invenio-deposit takes care of it via signal
        try:
            self.indexer.index(published_record)
        except RequestError:
            current_app.logger.exception(
                'Could not index {0}.'.format(published_record)
            )

        # We DONT rely on invenio-deposit's signal because we want
        # this method to be enough to publish a Record and perform all
        # associated work
        menrva_record_published.send(published_record['id'])

        return self

    def _prepare_edit(self, published_record):
        """Prepare the data for the edited record.

        Overrides parent's `_prepare_edit`.

        :param record: The published-record from which data should be
                       initially taken.
        """
        data = published_record.dumps()
        # Needed for merging. Interesting location for it though.
        data['_deposit']['pid']['revision_id'] = published_record.revision_id
        data['_deposit']['status'] = 'draft'
        data['type'] = RecordType.draft.value
        return data

    @has_status
    @preserve(result=False, fields=NON_FORM_FIELDS_TO_PRESERVE)
    def clear(self, *args, **kwargs):
        """Clear draft-record of all fields except for the specified ones.

        Overrides parent's `clear` to choose what to preserve.

        Status required: ``'draft'``.
        """
        super(Deposit, self).clear(*args, **kwargs)
