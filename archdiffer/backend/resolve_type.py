# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 14:01:49 2017

@author: pavla
"""

from .repository import repository

def resolve_type(compare_type, pkg1, pkg2):
    if compare_type in repository:
        repository[compare_type].compare(pkg1, pkg2)

