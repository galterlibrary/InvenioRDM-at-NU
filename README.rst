..
    Copyright (C) 2018 NU,FSM,GHSL.

    CD2H Repo Project is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

===================
 menRva
===================

Invenio-based Digital Library for the CD2H

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

1.  Start the celery worker via pipenv

    .. code-block:: console

        $ pipenv run celery worker --app invenio_app.celery --loglevel INFO

2.  ...in a new terminal, start the flask development server

    .. code-block:: console

        $ pipenv run ./scripts/server

This will start the Celery queue service in the background and the development
server at https://localhost:5000 .

Once you are done you can:

-   In the terminal where you started the celery worker

    .. code-block:: console

        ^C

-   ... in the new terminal where you started the development server

    .. code-block:: console

        ^C

If you want to permanently bring the containers down, you can do:

.. code-block:: console

    docker-compose down

To add another ``entry_point`` to the ``setup.py`` (to integrate a module) and
have it take effect:

1.  Modify ``setup.py``
2.  Stop the development server and/or celery service
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


Production (RHEL setup)
=======================

Enable SSH agent forwarding for <staging IP> and <production IP> on
your own machine:

.. code-block:: console

    Host <staging IP>
        ForwardAgent yes

    Host <production IP>
        ForwardAgent yes

Add the missing ``hosts`` file in ``deployment/ansible/`` and populate it with
the appropriate IPs:

.. code-block:: console

    stage ansible_host=<staging IP> ansible_user=deploy
    production ansible_host=<production IP> ansible_user=deploy

Add the missing ``daemon.json`` file in ``deployment/ansible/docker``
and populate it with your DNS IPs

.. code-block:: console

    {
      "live-restore": true,
      "group": "dockerroot",
      "dns": [<your DNS IPs>, "208.67.222.222", "8.8.8.8"]
    }

Finally, deploy the site via the ``scripts/deploy`` script :

.. code-block:: console

    $ pipenv run ./scripts/deploy stage master
    # For another <host> and <branch>
    $ pipenv run ./scripts/deploy <host> <branch>


Subsequent Deployments (updates)
--------------------------------

TODO: Automate updates

1.  ssh into production machine
2.  Run update script:

    .. code-block:: console

        docker exec -it cd2h-repo-project_web-ui_1 /bin/bash
        ./scripts/update

    This script should:

    * run DB migrations
    * run indexing updates
    * install missing requirements
