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

Further documentation is available on
https://cd2h-repo-project.readthedocs.io/


Development
===================

To run the project on your local development machine. Follow these
instructions:

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

2.  Start the containers for the services

    .. code-block::

        $ docker-compose up --detach

3.  Create a virtualenv (the name does not matter)

    .. code-block::

        $ mkvirtualenv my-repository-venv


4.  Start the celery worker

    .. code-block:: console

        $ workon my-repository-venv
        (my-repository-venv)$ celery worker --app invenio_app.celery --loglevel INFO

5.  ...in a new terminal, start the flask development server

    .. code-block:: console

        $ workon my-repository-venv
        (my-repository-venv)$ ./scripts/server

This will create and run 4 docker containers, will start the Celery queue service
and will start a development server on your host machine.

Once you are done you can:

-   Stop and remove the containers:

    .. code-block:: console

        docker-compose down

-   In the terminal where you started the celery worker

    .. code-block:: console

        ^C

-   ... in the new terminal where you started the development server

    .. code-block:: console

        ^C

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
