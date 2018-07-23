..
    Copyright (C) 2018 NU,FSM,GHSL.

    CD2H Repo Project is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

===================
 CD2H Repo Project
===================

.. image:: https://img.shields.io/travis/galterlibrary/cd2h-repo-project.svg
        :target: https://travis-ci.org/galterlibrary/cd2h-repo-project

.. image:: https://img.shields.io/coveralls/galterlibrary/cd2h-repo-project.svg
        :target: https://coveralls.io/r/galterlibrary/cd2h-repo-project

.. image:: https://img.shields.io/github/license/galterlibrary/cd2h-repo-project.svg
        :target: https://github.com/galterlibrary/cd2h-repo-project/blob/master/LICENSE

Invenio-based Digital Library for the CD2H

Documentation on Invenio is available on
https://invenio.readthedocs.io/en/latest/


Local Development
===================

Initial Setup
-------------

To setup the project on your local development machine, follow these
instructions. You only need to execute them once to setup your environment:

1.  On Linux, add the following to `/etc/sysctl.conf` on your local machine
    (host machine):

    .. code-block::

        # Memory mapped max size set for ElasticSearch
        vm.max_map_count=262144

    On macOS, do the following:

    .. code-block::

        screen ~/Library/Containers/com.docker.docker/Data/com.docker.driver.amd64-linux/tty
        # and in the shell
        sysctl -w vm.max_map_count=262144

2.  Create a virtualenv (the name does not matter)

    .. code-block::

        $ mkvirtualenv my-repository-venv

    This is one way to create such a Python virtual environment. There are other
    ways too.

3.  Install Python dependencies and current package

    Our project uses some of our private repositories. You will either need
    the `GITHUB_PRIVATE_TOKEN` value to download them or you can change the
    requirements.txt to clone the repositories directly.

    For the first option, you can ask your colleagues for the GITHUB_PRIVATE_TOKEN
    or you can find it on our Jenkins CI that uses it. Once you have that
    value, run:

    .. code-block::

        (my-repository-venv)$ GITHUB_PRIVATE_TOKEN=<retrieved value> pip install --requirement requirements.txt

    For the second option, for every line that contains
    `GITHUB_PRIVATE_TOKEN` in the `requirements.txt` file, replace it by:

    .. code-block::

        git+ssh://git@github.com/<owner>/<repo>.git@<tag>#egg=<desired egg name>

    where `<owner>`, `<repo>` and so on are taken from the line to be replaced.
    Then you should be able to install the dependencies in the
    `requirements.txt` file (given that you have access to our private repositories
    if you are reading this) by running:

    .. code-block::

        (my-repository-venv)$ pip install --requirement requirements.txt

    The `GITHUB_PRIVATE_TOKEN` value is sensitive, so it is not included in any
    repository.

    Irrespective of the option you chose above, install the current package
    after you installed the dependencies:

    .. code-block::

        (my-repository-venv)$ pip install --editable .[all]

4.  Execute the Invenio initial bootstrap and setup code in the virtual environment

    .. code-block::

        (my-repository-venv)$ ./scripts/bootstrap
        (my-repository-venv)$ ./scripts/setup

5.  Start the containers for the services

    .. code-block::

        $ docker-compose up --detach

    Note you don't have to be in a virtual environment to do so.
    This will create and run 4 docker containers. These containers will then
    keep themselves running even across reboots.

Day to day development
----------------------

Once you have setup your environment as above, your day to day work will
involve running these commands to develop / run the application on your local
machine.

1.  Start the celery worker inside your virtual environment

    .. code-block:: console

        $ workon my-repository-venv
        (my-repository-venv)$ celery worker --app invenio_app.celery --loglevel INFO

2.  ...in a new terminal, start the flask development server

    .. code-block:: console

        $ workon my-repository-venv
        (my-repository-venv)$ ./scripts/server

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


Continuous Integration (CI)
===================

To setup the CI machine, make sure it has enough virtual memory
for Elasticsearch. Add the following to `/etc/sysctl.conf` on the machine:

    .. code-block::

        # Memory mapped max size set for ElasticSearch
        vm.max_map_count=262144

To make the change immediate on a live machine:

    .. code-block::

        sysctl -w vm.max_map_count=262144


Production
===================

To setup the Production machine, make sure it has enough virtual memory
for Elasticsearch. Add the following to `/etc/sysctl.conf` on the machine:

    .. code-block::

        # Memory mapped max size set for ElasticSearch
        vm.max_map_count=262144

To make the change immediate on a live machine:

    .. code-block::

        sysctl -w vm.max_map_count=262144

Before you spin up all the production containers, retrieve the `GITHUB_PRIVATE_TOKEN`
value (see above) and export it to make it available at image build time. Run
`docker-compose` to spin everything up:

    .. code-block::

        GITHUB_PRIVATE_TOKEN=<value> docker-compose -f docker-compose.full.yml up --detach

If you rebuild an image (`docker build .`), the above `docker-compose` command
will pick it up!

# TODO: Remove the following by having the deployment script do it for us
After initial deployment, run the setup script:

    (virtualenv)$ ./scripts/setup

This script will build the database tables and initialize the index.
