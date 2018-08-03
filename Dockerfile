# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

# Multi-stage image creation
# This is the 2nd stage i.e. the Dockerfile for the actual running app.
# Multi-stage image creation is done to:
# - produce a Docker image containing no sensitive information
# - eventually slim down image size
# - (by-product) leverage layer caching for faster image builds
# - in 2 files because Docker 1.13 does not allow it in a single file
# It is done in 2 files because Docker 1.13 does not allow it in a single file.

FROM python:3.5

RUN apt-get update -y && apt-get upgrade -y

# Install needed tools
RUN curl --silent --location https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get install -y nodejs gdebi-core unzip

# Install Chrome+chromedriver
RUN curl --silent --remote-name --location https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN gdebi --non-interactive google-chrome-stable_current_amd64.deb
RUN curl --silent --remote-name --location https://chromedriver.storage.googleapis.com/2.40/chromedriver_linux64.zip
# Note that unzip has no long options
RUN unzip chromedriver_linux64.zip -d ${WORKING_DIR}/bin/

## Copy source code
ENV WORKING_DIR=/opt/cd2h-repo-project
RUN mkdir -p ${WORKING_DIR}/src
COPY ./ ${WORKING_DIR}/src
WORKDIR ${WORKING_DIR}/src

## Copy uwsgi config files
ENV INVENIO_INSTANCE_PATH=${WORKING_DIR}/var/instance
RUN mkdir -p ${INVENIO_INSTANCE_PATH}
COPY ./docker/uwsgi/ ${INVENIO_INSTANCE_PATH}

## Copy built dependencies from previous stage
COPY docker/build/site-packages /usr/local/lib/python3.5/site-packages
COPY docker/build/bin /usr/local/bin

## Install instance
RUN pip install -e .[all]
RUN ./scripts/bootstrap

# Set folder permissions
RUN chgrp -R 0 ${WORKING_DIR} && \
    chmod -R g=u ${WORKING_DIR}

RUN useradd invenio --uid 1000 --gid 0 && \
    chown -R invenio:root ${WORKING_DIR}
USER 1000

EXPOSE 5000
