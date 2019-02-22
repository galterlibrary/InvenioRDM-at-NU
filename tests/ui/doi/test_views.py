from datetime import datetime, timedelta

import pytest

from cd2h_repo_project.modules.doi.views import to_doi_field


@pytest.mark.parametrize('doi, timed_out, expect', [
    (
        '10.5072/qwer-tyui',
        False,
        ('<a href="https://doi.org/10.5072/qwer-tyui">'
         'https://doi.org/10.5072/qwer-tyui</a>')
    ),
    ('', False, 'Minting the DOI...'),
    (
        '',
        True,
        ('There was an issue minting the DOI. '
         '<a href="/contact-us">Contact us</a>.'),
    ),
    (
        '10.5072/qwer-tyui',
        True,
        ('<a href="https://doi.org/10.5072/qwer-tyui">'
         'https://doi.org/10.5072/qwer-tyui</a>')
    ),
])
def test_to_doi_field(
        doi, timed_out, expect, create_record, mocker, request_ctx):
    record = create_record()
    record['doi'] = doi
    if timed_out:
        patched_datetime = mocker.patch(
            'cd2h_repo_project.modules.doi.views.datetime',
        )
        patched_datetime.utcnow.return_value = (
            datetime.utcnow() + timedelta(hours=24)
        )

    result = to_doi_field(record)

    assert result == expect
