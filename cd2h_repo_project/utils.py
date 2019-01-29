"""General utility functions for any module."""
from flask_principal import AnonymousIdentity, Identity, RoleNeed, UserNeed


def get_identity(user):
    """Returns the identity for a given user instance.

    This is needed because we are more explicit then Flask-Principal
    and it is MUCH more convenient for tests.
    """
    if hasattr(user, 'id'):
        identity = Identity(user.id)
        identity.provides.add(UserNeed(user.id))
    else:
        return AnonymousIdentity()

    for role in getattr(user, 'roles', []):
        identity.provides.add(RoleNeed(role.name))

    identity.user = user
    return identity
