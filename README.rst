..
    Copyright (C) 2018 NU,FSM,GHSL.

    CD2H Repo Project is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

====================================
InvenioRDM @ Northwestern University
====================================

Invenio-based Digital Repository for the CD2H.

This is the repository for the code of the Center for Data to Health funded
project: https://github.com/data2health/InvenioRDM . Reporting will continue
on that repository, while this repository's code will over time be extracted
out in parts to https://github.com/inveniosoftware/invenio-app-rdm, our new
joint effort with CERN. We invite collaboration and discussion on that
repository. See you there!


Documentation on Invenio is available on
https://invenio.readthedocs.io/en/latest/


Local Development
===================

Initial Setup
-------------

To setup the project on your local development machine, follow these
instructions. You only need to execute them once to setup your environment:

1.  On Linux, add the following to ``/etc/sysctl.conf`` on your local machine
    (host machine):

    .. code-block:: console

        # Memory mapped max size set for ElasticSearch
        vm.max_map_count=262144

    On macOS, do the following:

    .. code-block:: console

        screen ~/Library/Containers/com.docker.docker/Data/com.docker.driver.amd64-linux/tty
        # and in the shell
        sysctl -w vm.max_map_count=262144

2.  Install the project locally:

    .. code-block:: console

        $ PIPENV_VENV_IN_PROJECT=1 pipenv sync --dev
        $ pipenv run pip install -r requirements-vcs.txt
        $ pipenv run pip install --editable .

    This will install the Python dependencies, then the dependencies that are
    just code held in version control systems and finally the project
    itself. The code has to be installed this way, because pipenv
    doesn't deal with the dependencies correctly at time of writing.

    Note: You may want to add ``PIPENV_VENV_IN_PROJECT=1`` to your shell
    (``.bashrc``, ``config.fish``...) for ease of use.

3.  Ask your colleagues for the current `.env` file and place it in the root
    directory of the project. This file contains the sensitive or
    "live specific" environment variables you will need.

4.  Start the containers for the services

    .. code-block:: console

        $ docker-compose up --build --detach

    Note you don't have to be in a virtual environment to do so.
    This will create and run 4 docker containers: database, queue,
    cache and search engine. These containers will then
    keep themselves running even across reboots.

5.  Execute the Invenio initial bootstrap and setup code

    .. code-block:: console

        $ pipenv run ./scripts/bootstrap
        $ pipenv run ./scripts/setup


Day to day development
----------------------

Once you have setup your environment as above, your day to day work will
involve running these commands to develop / run the application on your local
machine.

1.  Start the flask development server and celery worker via pipenv

    .. code-block:: console

        $ pipenv run ./scripts/server

This will start the Celery queue service in the background and the development
server at https://localhost:5000 .

Once you are done you can:

.. code-block:: console

    ^C

If you want to permanently bring the containers down, you can do:

.. code-block:: console

    docker-compose down

To add another ``entry_point`` to the ``setup.py`` (to integrate a module) and
have it take effect:

1.  Modify ``setup.py``
2.  Stop the scripts/server as above
3.  Re-install this project in your virtualenv:

    .. code-block:: console

        $ pipenv install --editable .

To run migrations, install new npm packages added via Bundles or collect/build
*new* assets:

.. code-block:: console

    $ pipenv run ./scripts/update

In development, after you have added a *new* template, you need to collect
it so that Flask can retrieve it. Once a template is collected (and linked),
any changes to it will be automatically picked up.

If you have local scripts you don't want to commit (yet!), place them in a
``_private/`` directory in an appropriate location. Tests are setup to ignore
directories named ``_private``.


Running a pull request locally
------------------------------

Sometimes you may want to pull down the branch associated with a pull request
to run the code locally. Here are the steps "typically" needed. In reality,
not all steps are required and they can usually be deduced from the
code changes.

1.  Reinstall the project's package

    .. code-block:: console

        pipenv install --editable .

    This is in case some of the ``entry_points`` in the ``setup.py`` have changed.

2.  Reinstall the project's Python dependencies

    .. code-block:: console

        pipenv sync --dev

    This will install the locked dependencies that are known to work. Run this
    if you see the ``Pipfile`` or ``Pipfile.lock`` files have changed.

3.  Reinstall the project's Python version control system (VCS) dependencies

    .. code-block:: console

        pipenv run pip install -r requirements-vcs.txt

    Run this if you see the ``requirements-vcs.txt`` file has changed.

4.  Run the ``scripts/update`` script

    .. code-block:: console

        pipenv run ./scripts/update

    This will create the ``package.json`` file with the npm dependencies and
    install them. It will also collect the Jinja2 templates, the static
    javascript and css/sass and bundle them. Finally it also runs database
    migrations. Whenever any of the above changes --which is pretty much all
    the time-- run this script.

5.  [Optional] Run added lines in the ``setup`` script

    If the ``scripts/setup`` file gets added commands, run those.

6.  [Exceptional] Uncomment the destructive commands from ``./scripts/setup``
    and run it

    .. code-block:: console

        pipenv run ./scripts/setup

    This is only to be done in rare cases, if there still seems to be issues.
    The database or index may be at fault then. Wipe them out to start from a
    clean slate.

That should cover it!

Running tests
-------------

To run regular tests (no end-to-end tests):

.. code-block:: console

    $ pipenv run ./run-tests.sh

To run end-to-end (E2E) tests (which are run by the CI):

Install the `Chrome browser <https://www.google.com/chrome/>`_ and
`chromedriver <https://chromedriver.storage.googleapis.com/2.40/chromedriver_linux64.zip>`_
on your machine to directories on your ``PATH``. This is a one-time setup.

Then, run the CI tests (they enable end-to-end testing):

.. code-block:: console

    $ pipenv run ./run-ci-tests.sh

Tests destroy the local Elasticsearch indices, to recreate them:

.. code-block:: console

    $ pipenv run scripts/reindex

This script re-indexes from the database.

Continuous Integration (CI)
===========================

To setup the CI machine, make sure it has enough virtual memory
for Elasticsearch. Add the following to ``/etc/sysctl.conf`` on the machine:

.. code-block:: console

    # Memory mapped max size set for ElasticSearch
    vm.max_map_count=262144

To make the change immediate on a live machine:

.. code-block:: console

    sysctl -w vm.max_map_count=262144


Production
==========

1.  Enable SSH agent forwarding for <staging IP> and <production IP> on
    your own machine in `~/.ssh/config`:

    .. code-block:: console

        Host <staging IP>
            ForwardAgent yes

        Host <production IP>
            ForwardAgent yes

2.  Add the missing ``hosts`` file in ``deployment/ansible/`` and populate it
    with the appropriate IPs:

    .. code-block:: console

        stage ansible_host=<staging IP> ansible_user=deploy
        production ansible_host=<production IP> ansible_user=deploy

3.  Add the missing ``daemon.json`` file in ``deployment/ansible/docker``
    and populate it with your DNS IPs

    .. code-block:: console

        {
          "live-restore": true,
          "group": "dockerroot",
          "dns": [<your DNS IPs>, "208.67.222.222", "8.8.8.8"]
        }

4.  Get your SSL certificates and private keys (`{stage, production}.cer`,
    `{stage, production}.key` and `{stage, production}.pem` files) from your
    colleagues and place them in `deployment/ansible/`.

5.  Create or get from your colleagues `stage.env` and `production.env` in
    `deployment/ansible/` for stage and production specific environment
    variables. Make sure `INVENIO_SECRET_KEY` is provided in each.

6.  Finally, deploy the site via the ``scripts/deploy`` script:

    .. code-block:: console

        $ pipenv run ./scripts/deploy stage master
        # For another <host> and <branch>
        $ pipenv run ./scripts/deploy <host> <branch>


Subsequent Deployments (updates)
--------------------------------

1.  `pipenv run ./scripts/deploy <host> <branch>`
