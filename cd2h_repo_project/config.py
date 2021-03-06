# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration for CD2H Repo Project.

As a hoster, before you deploy, set all the TODO::Hoster variables below. You
can overwrite them and set instance-specific configuration by providing a
`.env` file in the root directory with environment variables like so:

    ``INVENIO_<variable name>=<value>``
"""

from __future__ import absolute_import, print_function

import os
import sys
from datetime import timedelta

from invenio_indexer.api import RecordIndexer
from invenio_records_rest.facets import terms_filter
from invenio_records_rest.utils import allow_all, check_elasticsearch, deny_all

from cd2h_repo_project.modules.records.permissions import (
    CreatePermission, FilesPermission, edit_metadata_permission_factory,
    view_permission_factory
)
from cd2h_repo_project.modules.records.search import (
    RecordsSearch, nested_filter
)

# When run in a container (production-like-environments), the container
# infrastructure takes care of loading environment variables, but when
# running outside a container (development-like-environments) we need to do it
# ourselves. Since dotenv is only needed in a development environment, it is
# only installed in that environment.
try:
    from dotenv import load_dotenv
    load_dotenv(verbose=True)
except ImportError:
    pass


def _(x):
    """Identity function used to trigger string extraction."""
    return x


# Flask configuration
# ===================
# See details on
# https://flask.palletsprojects.com/en/master/config/

#: Secret key - each installation (dev, production, ...) needs a separate key.
#: It should be changed before deploying.
SECRET_KEY = 'CHANGE_ME'  # TODO::Hoster CONFIGURE
#: Max upload size for form data via application/mulitpart-formdata.
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MiB
#: Sets cookie with the secure flag by default
SESSION_COOKIE_SECURE = True
#: Since HAProxy and Nginx route all requests no matter the host header
#: provided, the allowed hosts variable is set to localhost. In production it
#: should be set to the correct host and it is strongly recommended to only
#: route correct hosts to the application.
APP_ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # TODO::Hoster CONFIGURE
PREFERRED_URL_SCHEME = 'https'

#: Custom constant for host name
#: Using Flask's SERVER_NAME breaks the containerized setup
SERVER_HOSTNAME = 'localhost:5000'  # TODO::Hoster CONFIGURE

# Rate limiting
# =============
#: Storage for ratelimiter.
RATELIMIT_STORAGE_URL = 'redis://localhost:6379/3'

# I18N
# ====
#: Default language
BABEL_DEFAULT_LANGUAGE = 'en'
#: Default time zone
BABEL_DEFAULT_TIMEZONE = 'America/Chicago'
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
#: Settings base template from invenio modules inherit from this.
SETTINGS_TEMPLATE = 'cd2hrepo_theme/page_settings.html'

# Theme configuration
# ===================
#: Site name
THEME_SITENAME = _('InvenioRDM @ Northwestern University')
#: Frontpage title.
THEME_FRONTPAGE_TITLE = _('InvenioRDM @ Northwestern University')
# THEME_HEADER_LOGIN_TEMPLATE = 'invenio_theme/header_login.html'

# Email configuration
# ===================
#: Email address used to send emails.
SUPPORT_EMAIL = ""  # TODO::Hoster CONFIGURE
#: Disable email sending by default.
MAIL_SUPPRESS_SEND = True  # TODO::Hoster set to False

# Assets
# ======
#: Static files collection method (defaults to copying files).
COLLECT_STORAGE = 'flask_collect.storage.link'  # TODO::Hoster set as below
# COLLECT_STORAGE = 'flask_collect.storage.file'  # in Production

# Uncomment to NOT bundle js and css in order to debug in the browser.
# ASSETS_DEBUG = True

# Accounts
# ========
#: Email address used as sender of account registration emails.
SECURITY_EMAIL_SENDER = SUPPORT_EMAIL  # TODO::Hoster CONFIGURE
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
# TODO::Hoster CONFIGURE
SQLALCHEMY_DATABASE_URI = (
    'postgresql+psycopg2://cd2h-repo-project:'
    'cd2h-repo-project@localhost/cd2h-repo-project'
)

# Digital Object Identifier (DOI), Datacite and Invenio-Pidstore integration
# =================================================
# TODO::Hoster CONFIGURE
DOI_REGISTER_SIGNALS = False
"""Set this to True to mint DOIs."""
DOI_PUBLISHER = "YOUR PLATFORM NAME"
"""REQUIRED if DOI_REGISTER_SIGNALS is True. Set this to your repository's
   institution or name."""
PIDSTORE_DATACITE_USERNAME = ''
"""REQUIRED if DOI_REGISTER_SIGNALS is True. Set this to your DataCite client
   account."""
PIDSTORE_DATACITE_PASSWORD = ''
"""REQUIRED if DOI_REGISTER_SIGNALS is True. Set this to your DataCite client
   account password."""
PIDSTORE_DATACITE_DOI_PREFIX = ''
"""REQUIRED if DOI_REGISTER_SIGNALS is True. Change this to your institution's
   DOI prefix."""
PIDSTORE_DATACITE_TESTMODE = True
"""Whether to interact with DataCite in test mode or not.
   Set to False in production"""
PIDSTORE_DATACITE_URL = "https://mds.datacite.org"
"""The DataCite minting endpoint."""

# JSONSchemas
# ===========
#: Hostname used in URLs for local JSONSchemas.
JSONSCHEMAS_HOST = 'localhost:5000'  # TODO::Hoster CONFIGURE
# Custom settings for our instance
DEPOSIT_JSONSCHEMAS_PREFIX = 'records/'
RECORD_JSONSCHEMAS_PREFIX = 'records/'
# Note: We set deposits and records to share the same schema
# because they should contain the same data. We allow the schema to be
# configurable (as per invenio-deposit) to give us some adaptability in the
# future.
RECORD_DEFAULT_JSONSCHEMA = 'records/record-v0.1.0.json'

# OAI-PMH
# =======
# TODO::Hoster CONFIGURE
OAISERVER_ID_PREFIX = 'oai:cd2hrepo.galter.northwestern.edu:'

# Debug
# =====
# Flask-DebugToolbar is by default enabled when the application is running in
# debug mode. More configuration options are available at
# https://flask-debugtoolbar.readthedocs.io/en/latest/#configuration

#: Switches off incept of redirects by Flask-DebugToolbar.
DEBUG_TB_INTERCEPT_REDIRECTS = False

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
            '*.matomo.cloud',
            "'unsafe-eval'",
        ],
    },
    'content_security_policy_report_uri': None,
    'content_security_policy_report_only': False,
    'session_cookie_secure': True,
    'session_cookie_http_only': True
}

# Invenio-Records
# ===============
# IMPORTANT NOTE: We collapse the user-interface for what Invenio calls a
#                 Record and what it calls a Deposit into a Record. This
#                 simplification makes it conceptually much simpler to work
#                 with these things and, especially, talk about them.
#                 In practice, this means the back-end keeps them separate
#                 so we can leverage what Invenio has done for us, but any
#                 external interface does not make the distinction Invenio
#                 makes about Records and Deposits: it is all Records for the
#                 onlooker. For us too, it is all Records conceptually.
#                 Behind-the-scenes, Invenio-Deposit deals with creating and
#                 editing; while Invenio-Record deals with viewing.

RECORDS_REST_ENDPOINTS = {
    'recid': {
        'pid_type': 'recid',
        'pid_minter': 'recid',  # Not used
        'pid_fetcher': 'recid',
        'default_endpoint_prefix': True,
        'search_class': RecordsSearch,
        'indexer_class': RecordIndexer,
        'search_index': 'records',
        'search_type': None,
        'record_serializers': {
            'application/json': (
                'cd2h_repo_project.modules.records.serializers:'
                'json_v1_response'
            )
        },
        'search_serializers': {
            'application/json': (
                'cd2h_repo_project.modules.records.serializers:json_v1_search'
            )
        },
        'record_loaders': {
            'application/json': (
                'cd2h_repo_project.modules.records.loaders:json_v1'
            )
        },
        'list_route': '/records/',  # all published records
        'item_route': '/records/<pid(recid):pid_value>',
        'default_media_type': 'application/json',
        'max_result_window': 10000,
        'error_handlers': {},
        # Records can only be created through the deposit API
        'create_permission_factory_imp': deny_all,
        'read_permission_factory_imp': view_permission_factory,
        # Records can only be updated through the deposit API
        'update_permission_factory_imp': deny_all,
        # We don't allow deletion for now
        'delete_permission_factory_imp': deny_all,
    },
}
"""REST API for Records."""

RECORDS_REST_FACETS = {
    # This is the name of the index/alias in ElasticSearch and not the pid type
    'records': {
        'aggs': {
            'authors': {  # Title-ized on the front-end to head the section
                # Needed bc 'authors' are *nested* objects
                # MenRvaJSONSerializer has been created to output
                # expected front-end format from this type of faceting
                'nested': {
                    'path': 'authors'
                },
                'aggs': {
                    'full_name': {
                        'terms': {'field': 'authors.full_name.raw'}
                    }
                }
            },
            'resource_type': {
                'terms': {'field': 'resource_type.general.raw'},
                'aggs': {
                    'rt_specific': {
                        'terms': {'field': 'resource_type.specific.raw'}
                    }
                }
            },
            'license': {
                'terms': {'field': 'license'}
            },
            'file_type': {
                # Dynamically creates a bucket for each unique `_files.type`
                'terms': {'field': '_files.type'},
            },
            'subjects': {
                # Needed bc 'terms' are *nested* objects
                # MenRvaJSONSerializer has been created to output
                # expected frontend format from this type of faceting
                'nested': {
                    'path': 'terms'
                },
                'aggs': {
                    'source': {
                        'terms': {'field': 'terms.source'},
                        'aggs': {
                            # Number records per source
                            'record_count': {
                                'reverse_nested': {}
                            },
                            # 'subject' rather than 'value' is used here
                            # bc these are not namespaced in the query string
                            'subject': {
                                'terms': {'field': 'terms.value'},
                                'aggs': {
                                    # Number records per value
                                    'record_count': {
                                        'reverse_nested': {}
                                    }
                                }
                            },
                        }
                    },
                }
            },
            # TODO: Add other facets here
        },
        # Filters the results further AFTER aggregation
        'post_filters': {
            'authors': nested_filter('authors', 'authors.full_name.raw'),
            'license': terms_filter('license'),
            'file_type': terms_filter('_files.type'),
            'subjects': nested_filter('terms', 'terms.source'),
            'subject': nested_filter('terms', 'terms.value'),
            'resource_type': terms_filter('resource_type.general.raw'),
            'rt_specific': terms_filter('resource_type.specific.raw'),
            # TODO: Add other post_filters here
        }
    }
}
"""REST facets for Records."""

RECORDS_REST_SORT_OPTIONS = {
    "records": {
        # Note that we have sort values for both asc and desc to workaround
        # a "separate ordering" bug in invenio-search-js.
        "bestmatch_desc": {  # 'sort' query string value: ?sort=bestmatch_desc
            "title": 'most relevant match',
            "fields": ['-_score'],
            "order": 1,
        },
        "bestmatch_asc": {
            "title": 'least relevant match',
            "fields": ['_score'],
            "order": 2,
        },
        "created_desc": {
            "title": 'most recently published',
            "fields": ['-_created'],
            "order": 3,
        },
        "created_asc": {
            "title": 'least recently published',
            "fields": ['_created'],
            "order": 4,
        },
        "updated_desc": {
            "title": 'most recently updated',
            "fields": ['-_updated'],
            "order": 5,
        },
        "updated_asc": {
            "title": 'least recently updated',
            "fields": ['_updated'],
            "order": 6,
        },
        "title_asc": {
            "title": 'title A to Z',
            "fields": ['title.raw'],
            "order": 7,
        },
        "title_desc": {
            "title": 'title Z to A',
            "fields": ['-title.raw'],
            "order": 8,
        }
    }
}
"""REST sort options per index."""

RECORDS_REST_DEFAULT_SORT = {
    "records": {
        "query": 'bestmatch_desc',
        "noquery": 'created_desc',
    }
}
"""Default sort option per index with/without query string."""

# Invenio-Records-UI
# ~~~~~~~~~~~~~~~~~~
RECORDS_UI_DEFAULT_PERMISSION_FACTORY = (
    'cd2h_repo_project.modules.records.permissions.view_permission_factory'
)
"""Default permission factory for viewing Records."""

RECORDS_UI_ENDPOINTS = {
    'recid': {
        'pid_type': 'recid',
        'route': '/records/<pid_value>',
        'template': 'records/view.html',
        'record_class': 'cd2h_repo_project.modules.records.api:Record',
    },
    'recid_files': {
        'pid_type': 'recid',
        'route': '/records/<pid_value>/files/<path:filename>',
        'view_imp': 'invenio_records_files.utils.file_download_ui',
        'record_class': 'cd2h_repo_project.modules.records.api:Record',
    },
}
"""UI endpoints for Records."""

PIDSTORE_RECID_FIELD = 'id'

# Invenio-Deposit
# ===============
# IMPORTANT NOTE: We collapse the user-interface for what Invenio calls a
#                 Record and what it calls a Deposit into a Record. This
#                 simplification makes it conceptually much simpler to work
#                 with these things and, especially, talk about them.
#                 In practice, this means the back-end keeps them separate
#                 so we can leverage what Invenio has done for us, but any
#                 external interface does not make the distinction Invenio
#                 makes about Records and Deposits: it is all Records for the
#                 onlooker. For us too, it is all Records conceptually.
#                 Behind-the-scenes, Invenio-Deposit deals with creating and
#                 editing; while Invenio-Record deals with viewing.
DEPOSIT_PID_MINTER = 'cd2h_recid'

DEPOSIT_DEFAULT_SCHEMAFORM = 'json/records/deposit_form.json'
"""Default Angular Schema **Form**.
"""

# TODO::Hoster set to JSONSCHEMAS_HOST
DEPOSIT_DEFAULT_JSONSCHEMA = RECORD_DEFAULT_JSONSCHEMA
"""Default JSON schema used for new deposits.
"""

_PID = (
    'pid(depid,record_class="cd2h_repo_project.modules.records.api:Deposit")'
)

# TODO: Grand: Merge DEPOSIT_REST_ENDPOINTS and RECORDS_REST_ENDPOINTS
#       Maintaining their inter-relationship is too much effort and they are
#       the same. But this is a lot of effort.
DEPOSIT_REST_ENDPOINTS = {
    'depid': {
        'pid_type': 'depid',
        'pid_minter': 'cd2h_depid',
        'pid_fetcher': 'deposit',
        'record_class': 'cd2h_repo_project.modules.records.api:Deposit',
        'record_loaders': {
            'application/json': (
                'cd2h_repo_project.modules.records.loaders:json_v1'
            )
        },
        'files_serializers': {
            'application/json': ('invenio_deposit.serializers'
                                 ':json_v1_files_response'),
        },
        'record_serializers': {
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        'search_class': (
            'cd2h_repo_project.modules.records.search:DepositsSearch'
        ),
        'search_serializers': {
            'application/json': (
                'cd2h_repo_project.modules.records.serializers:json_v1_search'
            ),
        },
        # TODO: -> /draft-records/ ?
        'list_route': '/deposits/',
        'indexer_class': None,
        'item_route': '/deposits/<{0}:pid_value>'.format(_PID),
        'file_list_route': '/deposits/<{0}:pid_value>/files'.format(_PID),
        'file_item_route':
            '/deposits/<{0}:pid_value>/files/<path:key>'.format(_PID),
        'default_media_type': 'application/json',
        'links_factory_imp': (
            'cd2h_repo_project.modules.records.links:deposit_links_api_factory'
        ),
        'create_permission_factory_imp': CreatePermission.create,
        'read_permission_factory_imp': edit_metadata_permission_factory,
        'update_permission_factory_imp': edit_metadata_permission_factory,
        # Deposits can't be deleted for now
        'delete_permission_factory_imp': deny_all,
        'max_result_window': 10000,
    },
}
"""Basic REST deposit configuration."""

DEPOSIT_RECORDS_UI_ENDPOINTS = {
    # TODO: Move this inside RECORDS_UI_ENDPOINTS?
    # NOTE: only import path strings are accepted
    'depid': {
        'pid_type': 'depid',
        'route': '/deposit/<pid_value>',  # To be consistent with JS route
        'template': 'records/edit.html',
        'record_class': 'cd2h_repo_project.modules.records.api:Deposit',
        'view_imp': 'cd2h_repo_project.modules.records.views.edit_view_method',
        'permission_factory_imp': 'cd2h_repo_project.modules.records'
                                  '.permissions'
                                  '.edit_metadata_permission_factory'
    },
}
"""Basic deposit UI endpoints configuration."""

DEPOSIT_UI_INDEX_URL = '/personal-records'
"""The UI endpoint for the index page."""

DEPOSIT_UI_INDEX_TEMPLATE = 'records/personal_records_search.html'
"""Template for list of deposits page."""

DEPOSIT_UI_NEW_URL = '/records/new'
"""The UI endpoint for the new deposit page."""

DEPOSIT_UI_NEW_TEMPLATE = 'records/edit.html'
"""Template for a new deposit page."""

DEPOSIT_UI_JSTEMPLATE_ACTIONS = 'templates/deposit/actions.html'
"""Template for <invenio-records-actions>."""

DEPOSIT_UI_JSTEMPLATE_ALERT = 'templates/deposit/alert.html'
"""Template for <invenio-records-alert>."""

DEPOSIT_UI_JSTEMPLATE_FILES_LIST = 'templates/deposit/files_list.html'
"""Template for <invenio-files-list>."""

DEPOSIT_UI_JSTEMPLATE_RESULTS = 'templates/search/personal_results.html'
"""Template for <invenio-search-results> of personal records."""

DEPOSIT_UI_JSTEMPLATE_UPLOAD = 'templates/deposit-form/upload.html'
"""Template for <invenio-files-list>."""

DEPOSIT_UI_RESPONSE_MESSAGES = {
    'self': {
        'message': (
            "Your Draft was saved successfully! Click 'Publish Record' to "
            "catalog it."
        )
    },
    'delete': {  # NOT USED
        'message': "Your entry was deleted successfully."
    },
    'discard': {  # NOT USED
        'message': "Your changes were discarded."
    },
    'publish': {
        'message': "Your Record was published successfully!"
    }
}

# NOTE: Unfortunately, we can't simply pick and choose deposit form elements
# templates from invenio-records-js, because we must specify one
# common parent directory. In other words, we can't pick templates in a
# directory in our repository and templates in a directory from
# invenio-records-js's repository. *All* templates must be under the same
# directory. So we copied the content of DEPOSIT_FORM_TEMPLATES_BASE and added
# our own templates.
DEPOSIT_FORM_TEMPLATES_BASE = 'templates/deposit-form'
"""Directory where the types used in deposit_form.json have their templates."""

DEPOSIT_FORM_TEMPLATES = {
    # Copied
    'array': 'array.html',
    'button': 'button.html',
    'default': 'default.html',
    'fieldset': 'fieldset.html',
    'radios': 'radios.html',
    'radios_inline': 'radios_inline.html',
    'select': 'select.html',
    'textarea': 'textarea.html',
    # Added
    'termsselect': 'termsselect.html',
    'uiselect': 'uiselect.html',
    'uiselectmultiple': 'uiselectmultiple.html',
}
"""Specific templates for the various deposit form elements."""

FILES_REST_PERMISSION_FACTORY = FilesPermission.create
"""Files REST permission factory"""

FIXTURES_FILES_LOCATION = 'data/'
"""Location where uploaded files are saved. If not an absolute path it is
   relative to instance path.
"""

FIXTURES_ARCHIVE_LOCATION = 'archive/'
"""Location where uploaded files are archived. If not an absolute path it is
   relative to instance path.
"""

# Search
# ======
SEARCH_UI_SEARCH_TEMPLATE = 'records/all_records_search.html'
SEARCH_UI_JSTEMPLATE_SEARCHBAR = 'templates/search/searchbar.html'
SEARCH_UI_JSTEMPLATE_COUNT = 'templates/search/count.html'
SEARCH_UI_JSTEMPLATE_SELECT_BOX = 'templates/search/sort_by.html'
SEARCH_UI_JSTEMPLATE_RESULTS = 'templates/search/results.html'
SEARCH_UI_JSTEMPLATE_FACETS = 'templates/search/facets.html'

# Contact Us
# ==========
CONTACT_US_SUPPORT_EMAIL_SUBJECT_TEMPLATE = 'contact_us/support_subject.txt'
CONTACT_US_SUPPORT_EMAIL_BODY_TEMPLATE_TXT = 'contact_us/support_body.txt'
CONTACT_US_SUPPORT_EMAIL_BODY_TEMPLATE_HTML = 'contact_us/support_body.html'

CONTACT_US_CONFIRMATION_EMAIL_SUBJECT_TEMPLATE = 'contact_us/confirmation_subject.txt'  # noqa
CONTACT_US_CONFIRMATION_EMAIL_BODY_TEMPLATE_TXT = 'contact_us/confirmation_body.txt'  # noqa
CONTACT_US_CONFIRMATION_EMAIL_BODY_TEMPLATE_HTML = 'contact_us/confirmation_body.html'  # noqa

# TODO::Hoster CONFIGURE
CONTACT_US_RECIPIENT_NAME = THEME_SITENAME
CONTACT_US_RECIPIENT_EMAIL = ''
CONTACT_US_SENDER_NAME = THEME_SITENAME
CONTACT_US_SENDER_EMAIL = ''

# Invenio-ldapclient
# ==================
LDAPCLIENT_LOGIN_USER_TEMPLATE = 'cd2hrepo_theme/login.html'
# TODO::Hoster CONFIGURE
LDAPCLIENT_SERVER_HOSTNAME = ''
LDAPCLIENT_USE_SSL = True
LDAPCLIENT_BIND_BASE = ''
LDAPCLIENT_SEARCH_BASE = ''
LDAPCLIENT_SERVER_PORT = 636

# Invenio-admin + Flask-admin
# ===========================
ADMIN_APPNAME = 'invenioRDM'
ADMIN_BASE_TEMPLATE = 'cd2hrepo_theme/page_admin.html'
ADMIN_PERMISSION_FACTORY = 'cd2h_repo_project.modules.admin.permissions.admin_permission_factory'  # noqa
"""Permission factory for the admin views."""

# Analytics
# =========
ANALYTICS_URL = ''  # TODO::Hoster: CONFIGURE
"""This is the URL provided by your analytics service without the starting
   `https://` and ending `/`.
   Example: For provided https://my-site.matomo.cloud/, use
   "my-site.matomo.cloud".
"""
ANALYTICS_SITEID = -1  # TODO::Hoster: CONFIGURE
"""Integer Site ID."""
