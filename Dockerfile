# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# Dockerfile for main CD2H-Repo-Project image

# TODO: Use python 3.6
FROM python:3.5

# Install needed tools
######################

# Update package list, upgrade current package and install new packages.
# These are all part of a single command to bust the cache when a package
# is added to the list.
RUN apt-get update && apt-get upgrade --yes && apt-get install --yes \
    git \
    gdebi-core \
    unzip \
    emacs-nox

RUN curl --silent --location https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get update && apt-get install --yes nodejs tree

# Setup Dockerfile and container run-time environment variables
ENV WORKING_DIR=/opt/cd2h-repo-project
ENV INVENIO_INSTANCE_PATH=${WORKING_DIR}/var/instance
# This will create the virtualenv locally (see below: ${WORKING_DIR}/src)
ENV PIPENV_VENV_IN_PROJECT=1

# Install Chrome+chromedriver
RUN curl --silent --remote-name --location https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN gdebi --non-interactive google-chrome-stable_current_amd64.deb
RUN curl --silent --remote-name --location https://chromedriver.storage.googleapis.com/2.40/chromedriver_linux64.zip
RUN mkdir -p ${WORKING_DIR}/bin
# Note that unzip has no long options
RUN unzip chromedriver_linux64.zip -d ${WORKING_DIR}/bin/

# Global python tools
RUN pip install --upgrade \
    setuptools \
    wheel \
    pip==18.1 \
    uwsgi \
    uwsgitop \
    uwsgi-tools \
    pipenv==2018.11.14

# Copy uwsgi config files (will typically not bust the cache)
# This only copies the files and NOT the directory itself
RUN mkdir -p ${INVENIO_INSTANCE_PATH}
COPY docker/uwsgi/ ${INVENIO_INSTANCE_PATH}

# Setup image build-time variable
## Since we are using a .env file for ALL our environment variables,
## we need to disable Flask's .env "tip"
ARG FLASK_SKIP_DOTENV
ARG INVENIO_COLLECT_STORAGE
ARG PIPENV_SYNC_OPTIONS

# Copy source code (this WILL bust the cache)
RUN mkdir -p ${WORKING_DIR}/src
COPY ./ ${WORKING_DIR}/src
WORKDIR ${WORKING_DIR}/src

# Install locked production dependencies
RUN pipenv sync ${PIPENV_SYNC_OPTIONS}

# Ensure database, task queue, elasticsearch are initialized
# and css + js is bundled
RUN pipenv run ./scripts/bootstrap

# Set folder permissions
RUN chgrp -R 0 ${WORKING_DIR} && \
    chmod -R g=u ${WORKING_DIR}

RUN useradd invenio --uid 1000 --gid 0 && \
    chown -R invenio:root ${WORKING_DIR}
USER 1000

EXPOSE 5000
