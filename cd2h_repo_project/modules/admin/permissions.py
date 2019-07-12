# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 - present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Permissions for Invenio-Admin."""

from invenio_access.permissions import Permission
from invenio_admin.permissions import action_admin_access


def admin_permission_factory(admin_view):
    """Factory for creating a permission for an admin.

    :param admin_view: Instance of administration view which is currently being
        protected.
    :returns: Permission instance.
    """
    return Permission(action_admin_access)
