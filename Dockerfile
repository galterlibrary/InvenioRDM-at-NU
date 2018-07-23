# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

FROM python:3.5 as builder

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y git
RUN pip install --upgrade setuptools wheel pip uwsgi uwsgitop uwsgi-tools pipenv

ARG GITHUB_PRIVATE_TOKEN
# Install dependencies
## Python
# TODO: Update to pipenv / Pipfile(.lock)
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Using a multi-stage build to:
# - produce a Docker image containing no sensitive information
# - eventually slim down image size
# - (by-product) leverages layer caching for faster image builds
FROM python:3.5

COPY --from=builder /usr/local/lib/python3.5/site-packages /usr/local/lib/python3.5/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

RUN apt-get update -y && apt-get upgrade -y

# Install needed tools
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get install -y nodejs gdebi-core unzip

# Install Chrome+chromedriver
RUN curl --silent --remote-name --location https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN gdebi --non-interactive google-chrome-stable_current_amd64.deb
RUN curl --silent --remote-name --location https://chromedriver.storage.googleapis.com/2.40/chromedriver_linux64.zip
# Note that unzip has no long options
RUN unzip chromedriver_linux64.zip -d ${WORKING_DIR}/bin/

# TODO: These are useless, remove
RUN python -m site
RUN python -m site --user-site

# Install Invenio
ENV WORKING_DIR=/opt/cd2h-repo-project
ENV INVENIO_INSTANCE_PATH=${WORKING_DIR}/var/instance

# copy everything inside /src
RUN mkdir -p ${WORKING_DIR}/src
COPY ./ ${WORKING_DIR}/src
WORKDIR ${WORKING_DIR}/src


# Install/create static files
RUN mkdir -p ${INVENIO_INSTANCE_PATH}
RUN pip install -e .[all]
RUN ./scripts/bootstrap

# copy uwsgi config files
COPY ./docker/uwsgi/ ${INVENIO_INSTANCE_PATH}

# Set folder permissions
RUN chgrp -R 0 ${WORKING_DIR} && \
    chmod -R g=u ${WORKING_DIR}

RUN useradd invenio --uid 1000 --gid 0 && \
    chown -R invenio:root ${WORKING_DIR}
USER 1000

EXPOSE 5000
