# -*- coding: utf-8 -*-
#
# This file is part of menRva.
# Copyright (C) 2018-present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""FAST term loader.

FAST stands for Faceted Application of Subject Terminology.
It is a simplified / optimized for faceting, controlled vocabulary derived from
the Library of Congress Subject Headings (LCSH).

The .nt (N-triple) file format this code reads can be downloaded here:
https://www.oclc.org/research/themes/data-science/fast/download.html
"""

import re
import zipfile
from zipfile import ZipFile

from rdflib.namespace import DCTERMS, SKOS
from rdflib.plugins.parsers.ntriples import NTriplesParser


class FAST(object):
    """FAST term extractor.

    Only extracts Topical terms for now.
    """

    IDENTIFIER_REGEX = r'fast/(\d+)'

    def __init__(self, terms=None):
        """Create instance.

        Only meant to be created via FAST.load and not on its own.
        """
        self.terms = terms if terms else []
        self.skip_identifier = None

    @classmethod
    def load(cls, filepath):
        """Return array of FAST dict. Main method."""
        if zipfile.is_zipfile(filepath):
            with ZipFile(filepath) as zf:
                nt_filename = next(
                    (n for n in zf.namelist() if n.endswith('.nt'))
                )
                # defaults to equivalent of 'rb'
                nt_file = zf.open(nt_filename)
        else:
            nt_file = open(filepath, 'rb')

        instance = cls()
        parser = NTriplesParser(instance)
        parser.parse(nt_file)

        nt_file.close()

        return instance.terms

    def triple(self, subject, predicate, obj):
        """Callback interface for NTriplesParser.

        This does the heavy lifting of:
            retrieving prefLabel
            filtering out obsoleted terms

        Relies on the fact that FAST N-triples are already grouped by
        identifier.
        """
        identifier = self.extract_identifier(subject)

        if not identifier or identifier == self.skip_identifier:
            return

        last_identifier = self._last_identifier()

        if identifier != last_identifier and predicate == SKOS.prefLabel:
            # TODO?: are Namedtuples more efficient here?
            self.terms.append({
                'identifier': identifier,
                'prefLabel': obj.value
            })
        elif predicate == DCTERMS.isReplacedBy:
            self.skip_identifier = identifier
            if last_identifier == self.skip_identifier:
                self.terms.pop()

    def extract_identifier(self, subject):
        """Return int identifier from subject or None if unable."""
        match = re.search(FAST.IDENTIFIER_REGEX, subject)
        if match:
            return int(match.group(1))

    def _last_identifier(self):
        """Return identifier of last element of terms.

        If terms is None returns None.
        """
        return self.terms[-1]['identifier'] if self.terms else None
