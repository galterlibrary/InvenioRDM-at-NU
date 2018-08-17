#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

export E2E=yes
# Print the image to console!
export E2E_OUTPUT='base64'
export PATH=${WORKING_DIR}/bin/:$PATH
pydocstyle cd2h_repo_project tests docs && \
isort --recursive --check-only --diff && \
python setup.py test
