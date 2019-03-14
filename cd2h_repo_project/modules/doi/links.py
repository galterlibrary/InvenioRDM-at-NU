"""DOI links."""


def doi_url_for(doi_value):
    """Return the URL for the DOI."""
    return 'https://doi.org/' + str(doi_value).strip('/')
