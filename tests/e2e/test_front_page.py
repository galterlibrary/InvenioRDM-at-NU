"""E2E test of the front page."""

from flask import current_app, url_for


def test_frontpage(live_server, browser):
    """Test retrieval of front page."""
    browser.get(url_for('cd2hrepo_frontpage.index', _external=True))

    search_form = browser.find_element_by_css_selector('form[role="search"]')
    assert search_form.get_attribute("action").endswith(
        current_app.config["THEME_SEARCH_ENDPOINT"]
    )

    create_button = browser.find_element_by_link_text('Catalog your Research')
    assert create_button.get_attribute("href").endswith(
        url_for('invenio_deposit_ui.new')
    )
