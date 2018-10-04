"""Data related commands to use on the command-line."""

from os import makedirs, stat
from os.path import exists

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_db import db
from invenio_files_rest.models import Location


def load_locations(force=False):
    """
    Load default file store and archive location.

    Lifted from https://github.com/zenodo/zenodo
    """
    try:
        locs = []
        uris = [
            ('default', True, current_app.config['FIXTURES_FILES_LOCATION'], ),
            ('archive', False,
             current_app.config['FIXTURES_ARCHIVE_LOCATION'], )
        ]
        for name, default, uri in uris:
            if uri.startswith('/') and not exists(uri):
                makedirs(uri)
            if not Location.query.filter_by(name=name).first():
                loc = Location(name=name, uri=uri, default=default)
                db.session.add(loc)
                locs.append(loc)

        db.session.commit()
        return locs
    except Exception:
        db.session.rollback()
        raise


@click.group()
def locations():
    """Deposit location commands.

    Usage on the command line becomes:

        cd2h-repo-project locations <command>

        OR (shorter)

        invenio locations <command>
    """
    pass


@locations.command('setup_storage')
@with_appcontext
def load_locations_cli():
    """
    Sets up where files are stored or archived.

    Lifted from https://github.com/zenodo/zenodo
    """
    locations = load_locations()
    click.secho(
        'Created location(s): {0}'.format([loc.uri for loc in locations]),
        fg='green'
    )
