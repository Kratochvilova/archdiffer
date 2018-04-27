#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Mon Mar  5 12:59:20 2018

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from ..database import Comparison, ComparisonType
from .. import constants
from . import request_parser

def get_first_key(dictionary, string):
    for key, value in dictionary.items():
        if value == string:
            return key
    return None

# Functions for making sets of filters
def comparisons(prefix='comparison_'):
    """Get filters for comparisons.

    :param string prefix: prefix of the name of the filter
    :return dict: dict of filters
    """
    filters = dict(
        **request_parser.equals(
            Comparison.id,
            name=prefix + 'id',
            function=(lambda x: int(x))
        ),
        **request_parser.equals(
            Comparison.state,
            name=prefix + 'state',
            function=(lambda x: get_first_key(constants.STATE_STRINGS, x))
        ),
        **request_parser.time(Comparison.time, name=prefix + 'time'),
        **request_parser.before(Comparison.time, name=prefix + 'before'),
        **request_parser.after(Comparison.time, name=prefix + 'after'),
    )
    return filters

def comparison_types(prefix='comparison_type_'):
    """Get filters for comparison types.

    :param string prefix: prefix of the name of the filter
    :return dict: dict of filters
    """
    filters = dict(
        **request_parser.equals(
            ComparisonType.id,
            name=prefix + 'id',
            function=(lambda x: int(x))
        ),
        **request_parser.equals(
            ComparisonType.name,
            name=prefix + 'name',
        ),
    )
    return filters
