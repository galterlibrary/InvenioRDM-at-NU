# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

FROM haproxy:1.8
RUN mkdir -p /usr/local/var/lib/haproxy/
COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg
# NOTE: You should have retrieved this file from your colleagues and Ansible
#       should have placed it in this folder.
#       Replace `private.pem` by `haproxy_cert.pem` for quick (insecure)
#       tire kicking.
COPY private.pem /usr/local/etc/cert.pem
RUN apt-get update && apt-get install --yes iputils-ping
