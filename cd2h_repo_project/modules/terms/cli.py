# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 - present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""MeSH cli commands."""
from os.path import dirname, join, realpath

import click
from elasticsearch.helpers import bulk
from flask.cli import with_appcontext
from invenio_search import current_search_client

from .fast import FAST
from .loaders import mesh_indexable
from .mesh import MeSH


@click.group()
def terms():
    """Invenio-terms commands."""
    pass


@terms.group()
def mesh():
    """Invenio-MeSH commands."""
    pass


DEFAULT_MESH_FILE = join(dirname(realpath(__file__)), 'data', 'd2018.bin')


@mesh.command('index')
@click.option('--source', '-s', default=DEFAULT_MESH_FILE)
@with_appcontext
def index_mesh(source):
    """Load MeSH terms to local index."""
    click.secho(
        'Loading MeSH topical headings from {}'.format(source), fg='blue'
    )

    terms = MeSH.load(source, filter='topics')

    # Adapt to indexer
    index_name = 'terms-term-v1.0.0'
    type_name = 'term-v1.0.0'
    indexable_terms = [
        mesh_indexable(t, index=index_name, doc_type=type_name) for t in terms
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


@terms.group()
def fast():
    """Invenio-FAST commands."""
    pass


NT_FAST_FILE = join(dirname(realpath(__file__)), 'data', 'FASTTopical.nt.zip')


@fast.command('index')
@click.option('--source', '-s', default=NT_FAST_FILE)
@with_appcontext
def index_fast(source):
    """Load FAST terms in memory for now. TODO: Index them."""
    terms = FAST.load(NT_FAST_FILE)

    print("First term:", terms[0])
    print("Last term:", terms[-1])
