# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 NU,FSM,GHSL.
#
# CD2H Repo Project is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest fixtures and plugins for the UI application."""

from __future__ import absolute_import, print_function

import os
from datetime import datetime

import pytest
from invenio_app.factory import create_app as create_ui_api
from selenium.webdriver import Chrome, ChromeOptions

SCREENSHOT_SCRIPT = """import base64
with open('screenshot.png', 'wb') as fp:
    fp.write(base64.b64decode('''{data}'''))
"""


@pytest.fixture(scope='module')
def create_app():
    """Create test app."""
    return create_ui_api


@pytest.fixture(scope='session')
def driver():
    """Selenium headless Chrome webdriver fixture.

    Code adapted from pytest-invenio/fixtures.py of package pytest-invenio.
    """
    # just Chrome for now
    options = ChromeOptions()
    options.headless = True
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    driver = Chrome(options=options)

    yield driver

    # Quit the webdriver instance
    driver.quit()


def _take_screenshot_if_test_failed(driver, request):
    """Take a screenshot if the test failed.

    Lifted from pytest-invenio/fixtures.py
    """
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        filename = '{modname}::{funname}::{now}.png'.format(
            modname=request.module.__name__,
            funname=request.function.__name__ if request.function else '',
            now=datetime.now().isoformat())
        filepath = os.path.join(_get_screenshots_dir(), filename)
        driver.get_screenshot_as_file(filepath)
        print("Screenshot of failing test:")
        if os.environ.get('E2E_OUTPUT') == 'base64':
            print(SCREENSHOT_SCRIPT.format(
                data=driver.get_screenshot_as_base64()))
        else:
            print(filepath)


def _get_screenshots_dir():
    """Create the screenshots directory.

    Lifted from pytest-invenio/fixtures.py
    """
    directory = ".e2e_screenshots"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


@pytest.fixture(scope='function')
def browser(driver, request):
    """Fixture for browser that takes a screenshot on error.

    .. code-block:: python

        from flask import url_for

        def test_browser(live_server, browser):
            browser.get(url_for('index', _external=True))

    The ``live_server`` fixture is provided by Pytest-Flask and uses the
    :py:data:`app` fixture to determine which application to start.

    .. note::

        End-to-end tests are only executed if the environment variable ``E2E``
        is set to yes::

            $ export E2E=yes

        This allows you to easily switch on/off end-to-end tests.

    In case the test fail, a screenshot will be taken and saved in folder
    ``.e2e_screenshots``.
    """
    yield driver
    _take_screenshot_if_test_failed(driver, request)
