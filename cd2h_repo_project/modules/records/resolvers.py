"""CD2H Record resolver."""

from invenio_pidstore.resolver import Resolver

from cd2h_repo_project.modules.records.api import Deposit, Record

record_resolver = Resolver(
    pid_type='recid', object_type='rec', getter=Record.get_record
)
"""'recid'-PID resolver for published Records.

.. code-block:: python

    record = record_resolver.resolve(recid_pid_value)
"""


deposit_resolver = Resolver(
    pid_type='depid', object_type='rec', getter=Deposit.get_record
)
"""'depid'-PID resolver for draft Records ie Deposits.

.. code-block:: python

    deposit = deposit_resolver.resolve(depid_pid_value)

"""
