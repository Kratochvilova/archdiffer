#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 12:59:20 2018

@author: pavla
"""

from ..database import Comparison, ComparisonType
from .. import constants
from . import request_parser

# Functions for making sets of filters
def comparisons(prefix='comparisons_'):
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
            function=(lambda x: constants.STATE_STRINGS.get(x))
        ),
        **request_parser.time(Comparison.time, name=prefix + 'time'),
        **request_parser.before(Comparison.time, name=prefix + 'before'),
        **request_parser.after(Comparison.time, name=prefix + 'after'),
    )
    return filters

def comparison_types(prefix='comparison_types_'):
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
