#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

pydocstyle cd2h_repo_project tests docs && \
isort --recursive --check-only --diff && \
# sphinx-build doesn't have long options for all short options
# -q : quiet,
# -n : nit-picky mode,
# -W : turn warnings into errors
sphinx-build -qnW --no-color docs docs/_build/html && \
python setup.py test
