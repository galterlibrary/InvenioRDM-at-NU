# -*- coding: utf-8 -*-
#
# This file is part of menRva.
# Copyright (C) 2018-present NU,FSM,GHSL.
#
# menRva is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""DOI utilities."""

from collections import defaultdict


def to_full_name(author):
    """Formats author name.

    Source of truth for author name formatting.
    """
    print("author", author)
    full_name = "{last_name}, {first_name} {middle_name}".format(
        **defaultdict(str, {k: v.title() for k, v in author.items()})
    )
    return full_name.strip()
