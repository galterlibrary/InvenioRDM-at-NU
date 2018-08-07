from flask import Blueprint


blueprint = Blueprint(
    'cd2hrepo_theme',
    __name__,
    template_folder='templates',
    static_folder='static',
)
"""Theme blueprint used to define template and static folders for the theme."""
