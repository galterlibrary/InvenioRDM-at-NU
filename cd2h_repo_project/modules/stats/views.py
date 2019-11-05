"""Example Module views."""

from flask import Blueprint, render_template

blueprint = Blueprint(
    'example_module',
    __name__,
    template_folder='templates',
    static_folder='static',
)
"""Example module blueprint used to define templates and static folders."""


@blueprint.route('/')
def view():
    """A view."""
    # TODO: Implement me!
    return render_template('example_module/index.html')
