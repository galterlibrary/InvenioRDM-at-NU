"""Test saved record i.e. record jsonschema is configured as expected."""

import pytest
from jsonschema.exceptions import ValidationError

# TODO: If tests too slow, restrict to jsonschema `validate`


def test_valid_terms(create_record):
    terms = [
        {'source': 'MeSH', 'value': 'Cognitive Neuroscience'}
    ]

    deposit = create_record({'terms': terms}, published=False)

    assert deposit['terms'] == terms


def test_invalid_structure_terms_should_error(create_record):
    terms = "invalid"

    with pytest.raises(ValidationError):
        deposit = create_record({'terms': terms}, published=False)


def test_missing_field_terms_should_error(create_record):
    terms = [
        {'source': 'MeSH'}
    ]

    with pytest.raises(ValidationError):
        deposit = create_record({'terms': terms}, published=False)


def test_added_field_terms_should_error(create_record):
    terms = [
        {'source': 'MeSH', 'value': 'Cognitive Neuroscience', 'bar': 'baz'}
    ]

    with pytest.raises(ValidationError):
        deposit = create_record({'terms': terms}, published=False)


def test_invalid_source_terms_should_error(create_record):
    terms = [
        {'source': 'BAZ', 'value': 'Cognitive Neuroscience'}
    ]

    with pytest.raises(ValidationError):
        deposit = create_record({'terms': terms}, published=False)


def test_valid_permissions(create_record):
    permissions = 'all_view'

    deposit = create_record({'permissions': permissions}, published=False)

    assert deposit['permissions'] == permissions


def test_invalid_permissions_should_error(create_record):
    permissions = 'all_read'

    with pytest.raises(ValidationError):
        deposit = create_record({'permissions': permissions}, published=False)


def test_valid_authors(create_record):
    authors = [
        {'first_name': 'John', 'last_name': 'Doe', 'full_name': 'Doe, John'}
    ]

    deposit = create_record({'authors': authors}, published=False)

    assert deposit['authors'] == authors


def test_invalid_authors_should_error(create_record):
    invalid_authors_list = [
        [{'last_name': 'Doe', 'full_name': 'Doe, John'}],
        [{'first_name': 'John', 'full_name': 'Doe, John'}],
        [{'first_name': 'John', 'last_name': 'Doe'}],
    ]

    for invalid_authors in invalid_authors_list:
        with pytest.raises(ValidationError):
            deposit = create_record(
                {'authors': invalid_authors},
                published=False
            )
