"""Theme blueprint in order for template and static files to be loaded."""

from flask import Blueprint
from invenio_admin import current_admin

blueprint = Blueprint(
    'cd2hrepo_theme',
    __name__,
    template_folder='templates',
    static_folder='static',
)
"""Theme blueprint used to define template and static folders for the theme."""

# Filters
# =======

@blueprint.app_template_filter('has_admin_access_permission')
def has_admin_access_permission(user):
    """Return True if current_user can access admin site.

    NOTE: `user` is not utilized, but it is kept for potential extensions
    """
    return (
        # We use below to keep in sync with admin permission_factory
        current_admin.permission_factory(current_admin.admin.index_view).can()
    )
