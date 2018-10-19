"""User dashboard views."""

from flask import Blueprint, render_template
from flask_login import login_required

blueprint = Blueprint(
    'user_dashboard',
    __name__,
    template_folder='templates',
    static_folder='static',
)
"""Theme blueprint used to define template and static folders for the theme."""


@blueprint.route('/account')
@login_required
def activity_feed():
    """List activities related to user. Act as user homepage."""
    # TODO: Implement me!
    return render_template('user_dashboard/activity_feed.html')
