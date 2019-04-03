"""Record module signals."""

from blinker import Namespace

_signals = Namespace()

menrva_record_published = _signals.signal('menrva-record-published')
"""Signal is sent after a deposit is published.

When implementing the event listener, the record data can be retrieved from
`sender`.

Example event listener (subscriber) implementation:

.. code-block:: python

    def listener(sender, *args, **kwargs):
        record = get_record_from_sender(sender)
        # do something with the record

    from cd2h_repo_project.modules.records.signals import (
        menrva_record_published
    )
    menrva_record_published.connect(listener)
"""
