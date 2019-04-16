# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""MeSH cli commands."""
from os.path import dirname, join, realpath

import click
from elasticsearch.helpers import bulk
from flask.cli import with_appcontext
from invenio_search import current_search_client

from .loaders import indexable
from .mesh import MeSH

DEFAULT_MESH_FILE = join(dirname(realpath(__file__)), 'd2018.bin')


@click.group()
def mesh():
    """Invenio-MeSH commands."""
    pass


@mesh.command('index')
@click.option('--source', '-s', default=DEFAULT_MESH_FILE)
@with_appcontext
def index(source):
    """Load MeSH terms to local index."""
    click.secho(
        'Loading MeSH topical headings from {}'.format(source), fg='blue'
    )

    terms = MeSH.load(source, filter='topics')

    # Adapt to indexer
    index_name = 'terms-term-v1.0.0'
    type_name = 'term-v1.0.0'
    indexable_terms = [
        indexable(t, index=index_name, doc_type=type_name) for t in terms
    ]

    # Index them
    es = current_search_client
    successes, errors = bulk(es, indexable_terms)
    es.indices.refresh(index=index_name)

    click.secho(
        'Loaded {loaded}/{total} MeSH topical headings from {source}'.format(
            loaded=successes, total=len(indexable_terms), source=source),
        fg='green'
    )

    if errors:
        click.secho('Errors:', fg='red')
        for error in errors:
            click.secho('{}'.format(error), fg='red')
