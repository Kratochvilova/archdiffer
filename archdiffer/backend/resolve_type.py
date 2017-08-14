# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 14:01:49 2017

@author: pavla
"""

from .repository import repository
from .. import database
from .config import DATABASE

def resolve_type(compare_type, pkg1, pkg2):
    if compare_type in repository:
        db = database.DatabaseConnection(DATABASE)
        return repository[compare_type].compare(db, pkg1, pkg2)

