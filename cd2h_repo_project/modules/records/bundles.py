"""Custom Record JS Bundles."""

from flask_assets import Bundle


js_deposit = Bundle(
    Bundle(
        'js/deposit/controllers.js',
        'js/deposit/filters.js',
        output="gen/cd2hrepo.deposit.filters.%(version)s.js",
        filters='jsmin',
    ),
    filters='jsmin',  # TODO: uglifyjs?
    output='gen/cd2hrepo.deposit.%(version)s.js',
)
"""Deposit JavaScript bundle.

Integrated via `'invenio_assets.bundles'` entrypoint in `setup.py`.
Assumes dependencies are satisfied by main default js bundle.
"""
