# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-based Digital Library for the CD2H"""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('cd2h_repo_project', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='cd2h-repo-project',
    version=version,
    description=__doc__,
    long_description=readme,
    keywords='cd2h-repo-project Invenio',
    license='MIT',
    author='NU,FSM,GHSL',
    author_email='piotr.hebal@northwestern.edu',
    url='https://github.com/galterlibrary/cd2h-repo-project',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_config.module': [
            'cd2h_repo_project = cd2h_repo_project.config',
        ],
        'console_scripts': [
            'menrva = invenio_app.cli:cli',
        ],
        'flask.commands': [
            'locations = cd2h_repo_project.modules.records.cli:locations',
            'mesh = cd2h_repo_project.modules.mesh.cli:mesh',
            'fast = cd2h_repo_project.modules.mesh.cli:fast',
        ],
        'invenio_base.blueprints': [
            'cd2h_repo_project = cd2h_repo_project.views:blueprint',
            'cd2hrepo_theme = cd2h_repo_project.modules.theme.views:blueprint',
            'cd2hrepo_frontpage = cd2h_repo_project.modules.frontpage.views:blueprint',
            'cd2hrepo_records = cd2h_repo_project.modules.records.views:blueprint',
            'cd2hrepo_user_dashboard = cd2h_repo_project.modules.user_dashboard.views:blueprint',
            'cd2hrepo_contact_us = cd2h_repo_project.modules.contact_us.views:blueprint',
            'cd2hrepo_doi = cd2h_repo_project.modules.doi.views:blueprint',
        ],
        'invenio_base.api_blueprints': [
            'menrva_mesh = cd2h_repo_project.modules.mesh.views:blueprint',
        ],
        'invenio_assets.bundles': [
            'cd2hrepo_theme_css = cd2h_repo_project.modules.theme.bundles:css',
            'cd2hrepo_theme_js = cd2h_repo_project.modules.theme.bundles:js',
            'cd2hrepo_deposit_js = cd2h_repo_project.modules.records.bundles:js_deposit',
            'cd2hrepo_search_js = cd2h_repo_project.modules.records.bundles:js_search',
        ],
        'invenio_i18n.translations': [
            'messages = cd2h_repo_project',
        ],
        'invenio_jsonschemas.schemas': [
            'cd2hrepo_records = cd2h_repo_project.modules.records.jsonschemas'
        ],
        'invenio_search.mappings': [
            'records = cd2h_repo_project.modules.records.mappings',
            'terms = cd2h_repo_project.modules.mesh.mappings'
        ],
        # Loaded when create_ui/create_app is used as application factory
        'invenio_base.apps': [
            'cd2hrepo_records = cd2h_repo_project.modules.records.ext:Records',
            'cd2hrepo_doi = cd2h_repo_project.modules.doi.ext:DigitalObjectIdentifier',
        ],
        # Loaded when create_api/create_app is used as application factory
        'invenio_base.api_apps': [
            'cd2hrepo_doi = cd2h_repo_project.modules.doi.ext:DigitalObjectIdentifier',
        ],
        'invenio_access.actions': [
          'cd2h-edit-metadata = cd2h_repo_project.modules.records.permissions:cd2h_edit_metadata',
        ],
        'invenio_pidstore.minters': [
            'cd2h_recid = cd2h_repo_project.modules.records.minters:mint_pids_for_record',
        ],
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 3 - Alpha',
    ],
)
