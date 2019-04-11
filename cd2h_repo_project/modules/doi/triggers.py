"""Signal listeners."""

from flask import current_app

from .tasks import register_doi


def doi_minting_trigger(recid_pid_value):
    """Triggers doi minting.

    :param recid_pid_value: record's PID value.
    """
    if current_app.config['DOI_REGISTER_SIGNALS']:
        register_doi.delay(recid_pid_value)
