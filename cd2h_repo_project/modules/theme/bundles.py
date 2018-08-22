"""JS/CSS bundles for theme."""

from flask_assets import Bundle
from invenio_assets import NpmBundle

css = NpmBundle(
    Bundle(
        'scss/styles.scss',
        filters='node-scss, cleancss',
        output="gen/cd2hrepo.local.styles.%(version)s.css",
    ),
    Bundle(
        'node_modules/angular-loading-bar/build/loading-bar.css',
        'node_modules/typeahead.js-bootstrap-css/typeaheadjs.css',
        'node_modules/bootstrap-switch/dist/css/bootstrap3'
        '/bootstrap-switch.css',
        filters='cleancss',
        output="gen/cd2hrepo.external.styles.%(version)s.css",
    ),
    depends=('scss/*.scss', ),
    output="gen/cd2hrepo.%(version)s.css",
    npm={
        'bootstrap-sass': '~3.3.5',
        'bootstrap-switch': '~3.0.2',
        'font-awesome': '~4.7.0',
        'typeahead.js-bootstrap-css': '~1.2.1',
    }
)
"""Default CSS bundle."""


js = Bundle(
    NpmBundle(
        'node_modules/almond/almond.js',
        'js/settings.js',
        filters='uglifyjs',
        output="gen/cd2hrepo.external.%(version)s.js",
        npm={
            'almond': '~0.3.1',
            'angular': '~1.4.9',
            'jquery': '~1.9.1',
        }
    ),
    Bundle(
        'js/base.js',
        output="gen/cd2hrepo.base.%(version)s.js",
        filters='requirejs',
    ),
    filters='jsmin',
    output='gen/packed.%(version)s.js',
)
"""Default JavaScript bundle with Almond, JQuery and RequireJS."""
