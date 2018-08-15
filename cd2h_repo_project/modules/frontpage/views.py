"""CD2HRepo frontpage blueprint."""

from flask import Blueprint, current_app, flash, render_template

blueprint = Blueprint(
    'cd2hrepo_frontpage',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@blueprint.route('/')
def index():
    """Frontpage blueprint."""
    msg = current_app.config.get('FRONTPAGE_MESSAGE')
    if msg:
        flash(msg, category=current_app.config.get(
            'FRONTPAGE_MESSAGE_CATEGORY', 'info'))

    return render_template('cd2hrepo_frontpage/index.html')
