# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test utilities.."""
from flask_security import login_user
from invenio_accounts.testutils import login_user_via_session


# TODO: potentially add this to pytest-invenio
def login_request_and_session(user, client):
    """Logs in the user in the current request AND the current session.

    We want to login without posting to 'ldap-login/', so that we don't depend
    on LDAP for tests. We want to be logged in on both the current request
    and the current session because a request context is pushed by the client
    fixture and the client needs to have its session logged in.
    """
    login_user(user, remember=True)
    login_user_via_session(client, email=user.email)
