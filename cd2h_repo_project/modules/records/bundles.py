"""Custom Record JS Bundles.

Integrate them by listing them in the `'invenio_assets.bundles'` entrypoint in
`setup.py`. Assumes dependencies are satisfied by main default js bundle.
"""

from flask_assets import Bundle

js_deposit = Bundle(
    Bundle(
        'js/deposit/controllers.js',
        'js/deposit/filters.js',
        filters='jsmin',
        output="gen/cd2hrepo.deposit.filters.%(version)s.js",
    ),
    filters='jsmin',
    output='gen/cd2hrepo.deposit.%(version)s.js',
)
"""Deposit JavaScript bundle."""

js_search = Bundle(
    Bundle(
        'js/search/filters.js',
        filters='jsmin',
        output="gen/cd2hrepo.search.filters.%(version)s.js",
    ),
    filters='jsmin',
    output='gen/cd2hrepo.search.%(version)s.js',
)
"""Records Search JavaScript bundle."""
