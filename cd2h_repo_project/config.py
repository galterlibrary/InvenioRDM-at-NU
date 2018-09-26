# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration for CD2H Repo Project.

You overwrite and set instance-specific configuration by either:

- Configuration file: ``<virtualenv prefix>/var/instance/invenio.cfg``
- Environment variables: ``APP_<variable name>``
"""

from __future__ import absolute_import, print_function

import os
import sys
from datetime import timedelta

from invenio_deposit.utils import check_oauth2_scope_write, \
    check_oauth2_scope_write_elasticsearch
from invenio_records_rest.utils import allow_all, check_elasticsearch


def _(x):
    """Identity function used to trigger string extraction."""
    return x


# Rate limiting
# =============
#: Storage for ratelimiter.
RATELIMIT_STORAGE_URL = 'redis://localhost:6379/3'

# I18N
# ====
#: Default language
BABEL_DEFAULT_LANGUAGE = 'en'
#: Default time zone
BABEL_DEFAULT_TIMEZONE = 'Europe/Zurich'
#: Other supported languages (do not include the default language in list).
I18N_LANGUAGES = [
    # ('fr', _('French'))
]

# Base templates
# ==============
#: Global base template.
BASE_TEMPLATE = 'cd2hrepo_theme/page.html'
#: Cover page base template (used for e.g. login/sign-up).
COVER_TEMPLATE = 'invenio_theme/page_cover.html'
#: Footer base template.
FOOTER_TEMPLATE = 'cd2hrepo_theme/footer.html'
#: Header base template.
HEADER_TEMPLATE = 'cd2hrepo_theme/header.html'
#: Settings base template.
SETTINGS_TEMPLATE = 'invenio_theme/page_settings.html'

# Theme configuration
# ===================
#: Site name
THEME_SITENAME = _('CD2H Repo Project')
#: Frontpage title.
THEME_FRONTPAGE_TITLE = _('CD2H Repo Project')
# THEME_HEADER_LOGIN_TEMPLATE = 'invenio_theme/header_login.html'

# Email configuration
# ===================
#: Email address for support.
SUPPORT_EMAIL = "piotr.hebal@northwestern.edu"
#: Disable email sending by default.
MAIL_SUPPRESS_SEND = True

# Assets
# ======
#: Static files collection method (defaults to copying files).
# COLLECT_STORAGE = 'flask_collect.storage.file'  # Production
COLLECT_STORAGE = 'flask_collect.storage.link'


# Accounts
# ========
#: Email address used as sender of account registration emails.
SECURITY_EMAIL_SENDER = SUPPORT_EMAIL
#: Email subject for account registration emails.
SECURITY_EMAIL_SUBJECT_REGISTER = _("Welcome to CD2H Repo Project!")
#: Redis session storage URL.
ACCOUNTS_SESSION_REDIS_URL = 'redis://localhost:6379/1'

# Celery configuration
# ====================

BROKER_URL = 'amqp://guest:guest@localhost:5672/'
#: URL of message broker for Celery (default is RabbitMQ).
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672/'
#: URL of backend for result storage (default is Redis).
CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'
#: Scheduled tasks configuration (aka cronjobs).
CELERY_BEAT_SCHEDULE = {
    'indexer': {
        'task': 'invenio_indexer.tasks.process_bulk_queue',
        'schedule': timedelta(minutes=5),
    },
    'accounts': {
        'task': 'invenio_accounts.tasks.clean_session_table',
        'schedule': timedelta(minutes=60),
    },
}

# Database
# ========
#: Database URI including user and password
SQLALCHEMY_DATABASE_URI = (
    'postgresql+psycopg2://cd2h-repo-project:'
    'cd2h-repo-project@localhost/cd2h-repo-project'
)

# JSONSchemas
# ===========
#: Hostname used in URLs for local JSONSchemas.
JSONSCHEMAS_HOST = 'cd2hrepo.galter.northwestern.edu'

# Flask configuration
# ===================
# See details on
# http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values

#: Secret key - each installation (dev, production, ...) needs a separate key.
#: It should be changed before deploying.
SECRET_KEY = 'CHANGE_ME'
#: Max upload size for form data via application/mulitpart-formdata.
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MiB
#: Sets cookie with the secure flag by default
SESSION_COOKIE_SECURE = True
#: Since HAProxy and Nginx route all requests no matter the host header
#: provided, the allowed hosts variable is set to localhost. In production it
#: should be set to the correct host and it is strongly recommended to only
#: route correct hosts to the application.
APP_ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# OAI-PMH
# =======
OAISERVER_ID_PREFIX = 'oai:cd2hrepo.galter.northwestern.edu:'

# Debug
# =====
# Flask-DebugToolbar is by default enabled when the application is running in
# debug mode. More configuration options are available at
# https://flask-debugtoolbar.readthedocs.io/en/latest/#configuration

#: Switches off incept of redirects by Flask-DebugToolbar.
DEBUG_TB_INTERCEPT_REDIRECTS = False

# TODO: Review security policies so that we can develop locally correctly
APP_DEFAULT_SECURE_HEADERS = {
    'force_https': True,
    'force_https_permanent': False,
    'force_file_save': False,
    'frame_options': 'sameorigin',
    'frame_options_allow_from': None,
    'strict_transport_security': True,
    'strict_transport_security_preload': False,
    'strict_transport_security_max_age': 31556926,  # One year in seconds
    'strict_transport_security_include_subdomains': True,
    'content_security_policy': {
        'default-src': [
            "'self'",
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com',
            "'unsafe-eval'",
        ],
    },
    'content_security_policy_report_uri': None,
    'content_security_policy_report_only': False,
    'session_cookie_secure': True,
    'session_cookie_http_only': True
}

# Invenio-Deposit and CD2H-datamodel
# ==================================
# TODO: Setup this configuration in cd2h_datamodel/config.py
#       and override if need be here
DEPOSIT_DEFAULT_SCHEMAFORM = 'json/cd2h_datamodel/deposit_form.json'
"""Default Angular Schema **Form** provided by external package cd2h_datamodel.
"""

DEPOSIT_DEFAULT_JSONSCHEMA = 'records/record-v0.1.0.json'
"""Default JSON schema used for new deposits.
"""

_PID = 'pid(depid,record_class="cd2h_datamodel.api:Deposit")'

DEPOSIT_REST_ENDPOINTS = {
    'depid': {
        'pid_type': 'depid',
        'pid_minter': 'deposit',
        'pid_fetcher': 'deposit',
        'record_class': 'cd2h_datamodel.api:Deposit',
        'record_loaders': {
            'application/json': 'cd2h_datamodel.loaders:json_v1',
        },
        'files_serializers': {
            'application/json': ('invenio_deposit.serializers'
                                 ':json_v1_files_response'),
        },
        'record_serializers': {
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        'search_class': 'invenio_deposit.search:DepositSearch',
        'search_serializers': {
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
        },
        'list_route': '/deposits/',
        'indexer_class': None,
        'item_route': '/deposits/<{0}:pid_value>'.format(_PID),
        'file_list_route': '/deposits/<{0}:pid_value>/files'.format(_PID),
        'file_item_route':
            '/deposits/<{0}:pid_value>/files/<path:key>'.format(_PID),
        'default_media_type': 'application/json',
        'links_factory_imp': 'cd2h_datamodel.links:deposit_links_factory',
        # TODO: Redefine these permissions to cover our auth needs
        'create_permission_factory_imp': allow_all,
        'read_permission_factory_imp': check_elasticsearch,
        'update_permission_factory_imp': allow_all,
        'delete_permission_factory_imp': allow_all,
        'max_result_window': 10000,
    },
}
"""Basic REST deposit configuration."""

#: Files REST permission factory
FILES_REST_PERMISSION_FACTORY = \
    'cd2h_datamodel.permissions:files_permission_factory'

FIXTURES_FILES_LOCATION = os.path.join(sys.prefix, 'var/instance/data')
"""Location where uploaded files are saved"""

FIXTURES_ARCHIVE_LOCATION = os.path.join(sys.prefix, 'var/instance/archive')
"""Location where uploaded files are archived"""

# Uncomment to NOT bundle js and css in order to debug in the browser.
# ASSETS_DEBUG = True

# Search
# ======
SEARCH_UI_SEARCH_TEMPLATE = 'cd2h_datamodel/search.html'
SEARCH_UI_JSTEMPLATE_RESULTS = 'templates/cd2h_datamodel/results.html'
