#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  7 15:44:13 2018

@author: pavla
"""

from ... import database
from . import rpm_db_models
from .constants import COMPARISON_TYPE

def init_db():
    """Initialize database: create tables according to rpmdiff models;
    create comparison type for rpmdiff.
    """
    database.Base.metadata.create_all(database.engine())
    
    session = database.session()
    if session.query(database.ComparisonType).filter_by(
            name=COMPARISON_TYPE
    ).one_or_none() is None:
        session.add(database.ComparisonType(name=COMPARISON_TYPE))
        session.commit()
