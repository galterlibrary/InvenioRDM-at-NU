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

To run the project on your local development machine:

    # Create a virtualenv (the name does not matter)
    mkvirtualenv my-repository-venv

    # Start the containers for the services
    docker-compose up --detach

    # Start the celery worker
    $ workon my-repository-venv
    (my-repository-venv)$ celery worker --app invenio_app.celery --loglevel INFO

    # ...in a new terminal, start the flask development server
    $ workon my-repository-venv
    (my-repository-venv)$ ./scripts/server

This will create and run 4 docker containers, will start the Celery queue service
and will start a development server on your host machine.

Once you are done you can:

    # Stop and remove the containers:
    docker-compose down

    # In the terminal where you started the celery worker
    ^C

    # ... in the new terminal where you started the development server
    ^C

Continuous Integration
===================

Set enough virtual memory for Elasticsearch

    sysctl -w vm.max_map_count=262144


Production
===================

Set enough virtual memory for Elasticsearch

    sysctl -w vm.max_map_count=262144

