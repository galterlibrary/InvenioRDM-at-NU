# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# Dockerfile for main CD2H-Repo-Project image
#
# ENV sets up Dockerfile and container run-time environment variables
# ARG sets up build-time variables (NOT available at run-time)
#
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
    emacs-nox \
    cowsay
# NOTE: Add or remove cowsay from the above list to force refresh of libraries

RUN curl --silent --location https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get update && apt-get install --yes nodejs tree

# Install Chrome+chromedriver
# TODO: update urls
RUN curl --silent --remote-name --location https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN gdebi --non-interactive google-chrome-stable_current_amd64.deb
RUN curl --silent --remote-name --location https://chromedriver.storage.googleapis.com/2.40/chromedriver_linux64.zip

ENV WORKING_DIR=/opt/cd2h-repo-project

# Note that unzip has no long options
RUN mkdir -p ${WORKING_DIR}/bin
RUN unzip chromedriver_linux64.zip -d ${WORKING_DIR}/bin/

# Global python tools
RUN pip install --upgrade \
    setuptools \
    wheel \
    pip==19.2 \
    pipenv==2018.11.26 \
    uwsgi

# Copy uwsgi config files (will typically not bust the cache)
# This only copies the files and NOT the directory itself
ENV INVENIO_INSTANCE_PATH=${WORKING_DIR}/var/instance
RUN mkdir -p ${INVENIO_INSTANCE_PATH}
COPY docker/uwsgi/ ${INVENIO_INSTANCE_PATH}

# Setup image build-time variable
## Since we are using a .env file for ALL our environment variables,
## we need to disable Flask's .env "tip"
ARG FLASK_SKIP_DOTENV
ARG INVENIO_COLLECT_STORAGE
ARG PIPENV_SYNC_OPTIONS

RUN mkdir -p ${WORKING_DIR}/src

# Create mount points for volumes
RUN mkdir ${INVENIO_INSTANCE_PATH}/static
RUN mkdir ${INVENIO_INSTANCE_PATH}/data
RUN mkdir ${INVENIO_INSTANCE_PATH}/archive

# Install global nodejs tools
## Reset global npm location to avoid permission issues
ENV NPM_CONFIG_PREFIX=${INVENIO_INSTANCE_PATH}/.npm-global
RUN mkdir ${NPM_CONFIG_PREFIX}
RUN npm config set prefix ${NPM_CONFIG_PREFIX}
ENV PATH=${NPM_CONFIG_PREFIX}/bin:$PATH
RUN npm update  && \
    npm install --global --unsafe-perm \
    node-sass@4.9.0 clean-css@3.4.19 uglify-js@2.7.3 requirejs@2.2.0

# Set folder permissions
RUN chgrp -R 0 ${WORKING_DIR} && \
    chmod -R g=u ${WORKING_DIR}
RUN useradd invenio --uid 1000 --gid 0 --create-home && \
    chown -R invenio:root ${WORKING_DIR}

# Install locked production dependencies now to speed up build
# (by having this step cached)
COPY Pipfile Pipfile.lock requirements-vcs.txt ${WORKING_DIR}/src/
WORKDIR ${WORKING_DIR}/src
# This will create the virtualenv locally (see below: ${WORKING_DIR}/src)
ENV PIPENV_VENV_IN_PROJECT=1
RUN pipenv sync ${PIPENV_SYNC_OPTIONS}
RUN pipenv run pip install -r requirements-vcs.txt

# Copy source code (this WILL bust the cache)
COPY ./ ${WORKING_DIR}/src

# Install project (use pip so project is NOT added to Pipfile)
RUN pipenv run pip install .

USER 1000
EXPOSE 5000
