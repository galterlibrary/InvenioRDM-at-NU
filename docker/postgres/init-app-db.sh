#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE ROLE cd2h-repo-project WITH LOGIN PASSWORD 'cd2h-repo-project';
    ALTER ROLE cd2h-repo-project CREATEDB;
    \du;
EOSQL
