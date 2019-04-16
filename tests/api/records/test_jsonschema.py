"""Test the configured record jsonschema is as expected."""

import pytest
from jsonschema.exceptions import ValidationError

from cd2h_repo_project.modules.records.api import Deposit

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
