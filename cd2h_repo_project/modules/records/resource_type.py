# -*- coding: utf-8 -*-
#
# This file is part of menRva.
# Copyright (C) 2018-present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Resource Type Object."""

import csv
from os.path import dirname, join, realpath


class ResourceType(object):
    """Resource Type.

    If resource types in static/json/records/deposit_form.json changes, this
    must change as well.
    """

    RESOURCE_TYPES = {
        'dataset': ['dataset'],
        'articles': [
            'book review',
            'data paper',
            'editorial',
            'journal article',
            'letter to the editor',
            'newspaper article',
            'research paper',
            'retraction',
            'review article',
            'software paper',
        ],
        'conference objects': [
            'conference paper',
            'conference presentation',
            'conference proceeding',
            'congress',
            'meeting abstract',
            'poster',
        ],
        'images': [
            'architectural drawing',
            'chart',
            'drawing',
            'map',
            'photograph',
            'pictorial work',
            'portrait',
        ],
        'multimedia': [
            'animation',
            'audio recording',
            'database',
            'postcard',
            'social media',
            'software or program code',
            'video',
            'website',
        ],
        'periodicals': [
            'journal',
            'magazine',
            'newsletter',
            'newspaper',
        ],
        'books': [
            'account book',
            'almanac',
            'atlas',
            'biography',
            'book',
            'catalog',
            'diary',
            'handbook',
            'part of book',
        ],
        'study documentation': [
            'case reports',
            'clinical study',
            'clinical trial',
            'comparative study',
            'data management plan',
            'evaluation study',
            'research proposal',
            'statistics',
        ],
        'theses and dissertations': [
            'academic dissertations',
            'thesis bachelor',
            'thesis masters',
            'thesis doctoral',
        ],
        'text resources': [
            'abstract',
            'advertisement',
            'bibliography',
            'biobibliography',
            'comment',
            'correspondence',
            'fictional work',
            'form',
            'guideline',
            'letter',
            'manuscript',
            'patent',
            'patient education handout',
            'personal narrative',
            'poetry',
            'preprint',
            'program',
            'resource guide',
            'software documentation',
            'speech',
            'technical documentation',
            'working paper',
        ],
        'learning objects': [
            'examination questions',
            'lecture',
            'lecture notes',
            'lesson',
            'presentation',
            'problems and exercises',
        ],
        'archival items': [
            'collection',
            'ephemera',
            'exhibitions',
        ],
        'other': [
            'annual report',
            'capstone project',
            'interview',
            'laboratory manual',
            'table',
            'technical report',
            'other',
        ]
    }

    def __init__(self, general, specific):
        """Constructor."""
        self.general = general
        self.specific = specific

    @classmethod
    def get(cls, general, specific):
        """Returns a ResourceType."""
        if specific in cls.RESOURCE_TYPES.get(general, []):
            return cls(general, specific)

    def map(self, mapping):
        """Returns the corresponding value in `mapping`."""
        return mapping.get((self.general, self.specific))


class ResourceTypeHierarchy(object):
    """Hierarchy Mapping."""

    def __init__(self):
        """Constructor."""
        self.filename = join(
            dirname(realpath(__file__)), 'data', 'resource_type_mapping.csv'
        )
        with open(self.filename) as f:
            reader = csv.DictReader(f)
            self.map = {
                (row['Group'].lower(), row['Name'].lower()):
                [
                    e.strip().lower() for e in row['Hierarchy'].split(",")
                ] + [row['Name'].lower()]
                for row in reader
            }

    def get(self, key, default=None):
        """Return the mapped value.

        `key` is (<general resource type>, <specific resource type>).
        """
        return self.map.get(key, default)
