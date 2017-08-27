# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 14:01:49 2017

@author: pavla
"""

from ..repository import comparators

def resolve_type(comparator, pkg1, pkg2):
    if comparator in comparators:
        comparators[comparator](pkg1, pkg2)

