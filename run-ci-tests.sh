#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

# TODO: Enable End-to-End testing with headless chrome/firefox
# export E2E=yes
# export PATH=$WORKING_DIR/bin/:$PATH

pydocstyle cd2h_repo_project tests docs && \
# TODO: replace with flake8 and flake8-import?
isort --recursive --check-only --diff && \
python setup.py test
