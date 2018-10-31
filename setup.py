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

DATABASE = "postgresql"
ELASTICSEARCH = "elasticsearch6"
INVENIO_VERSION = "3.0.0"

tests_require = [
    'check-manifest>=0.35',
    'coverage>=4.4.1',
    'isort>=4.3',
    'mock>=2.0.0',  # TODO: Remove bc we only support Python 3
    'pydocstyle>=2.0.0',
    # TODO: Add pytest-cache?
    'pytest-cov>=2.5.1',
    'pytest-invenio>=1.0.2,<1.0.5',
    'pytest-mock>=1.6.0',
    'pytest-pep8>=1.0.6',
    'pytest>=3.3.1',
    'selenium>=3.4.3',
    'pytest-flask==0.12.0'  # Artificially added
]

extras_require = {
    'docs': [
        'Sphinx>=1.5.1',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=2.4.0',
    'pytest-runner>=3.0.0,<5',
]

install_requires = [
    'Flask-BabelEx>=0.9.3',
    'Flask-Debugtoolbar>=0.10.1',
    'invenio[{db},{es},base,auth,metadata]~={version}'.format(
        db=DATABASE, es=ELASTICSEARCH, version=INVENIO_VERSION),
    'invenio-records-rest>=1.1.0,<1.2.0',
    'arrow>=0.12.1',
    'IPython<7.0.0',
    # TODO: Move to pipenv completely and set a non-prerelease version
    #       to invenio-deposit
    'SQLAlchemy-Continuum==1.3.4',
    'marshmallow==2.15.5',
]

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
            'cd2h-repo-project = invenio_app.cli:cli',
        ],
        'flask.commands': [
            'locations = cd2h_repo_project.modules.records.cli:locations',
        ],
        'invenio_base.blueprints': [
            'cd2h_repo_project = cd2h_repo_project.views:blueprint',
            'cd2hrepo_theme = cd2h_repo_project.modules.theme.views:blueprint',
            'cd2hrepo_frontpage = cd2h_repo_project.modules.frontpage.views:blueprint',
            'cd2hrepo_records = cd2h_repo_project.modules.records.views:blueprint',
        ],
        'invenio_assets.bundles': [
            'cd2hrepo_theme_css = cd2h_repo_project.modules.theme.bundles:css',
            'cd2hrepo_theme_js = cd2h_repo_project.modules.theme.bundles:js',
            'cd2hrepo_deposit_js = cd2h_repo_project.modules.records.bundles:js_deposit',
        ],
        'invenio_i18n.translations': [
            'messages = cd2h_repo_project',
        ],
        'invenio_jsonschemas.schemas': [
            'cd2hrepo_records = cd2h_repo_project.modules.records.jsonschemas'
        ],
        'invenio_search.mappings': [
            'records = cd2h_repo_project.modules.records.mappings'
        ],
        'invenio_base.apps': [
            'cd2hrepo_records = cd2h_repo_project.modules.records.ext:Records',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
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
