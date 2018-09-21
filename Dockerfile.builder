# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

# Multi-stage image creation
# This is the 1st stage i.e. the Dockerfile for the container that will build
# the requirements to a directory and from which directory the second
# Dockerfile will start to configure and run the app.
# Multi-stage image creation is done to:
# - produce a Docker image containing no sensitive information
# - eventually slim down image size
# - (by-product) leverage layer caching for faster image builds
# It is done in 2 files because Docker 1.13 does not allow it in a single file.

# USAGE:
# docker build --build-arg GITHUB_PRIVATE_TOKEN=<value> -f Dockerfile.builder -t cd2h-repo-builder .
FROM python:3.5

# Update package list, upgrade current package and install new packages
# all in one line to bust the cache when a package is added to the list
RUN apt-get update && apt-get upgrade --yes && apt-get install --yes \
    git

RUN pip install --upgrade \
    setuptools \
    wheel \
    pip==18.0 \
    uwsgi \
    uwsgitop \
    uwsgi-tools \
    pipenv==2018.7.1

# Install Python dependencies to hide sensitive information from final image
# Busts the cache ONLY IF requirements.txt changes
# TODO: Update to pipenv / Pipfile(.lock)
ARG GITHUB_PRIVATE_TOKEN
COPY requirements.txt ./
RUN pip install -r requirements.txt
