#!/usr/bin/python3
# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Wed Oct  4 14:02:49 2017

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from archdiffer import database
from archdiffer.plugins.rpmdiff import rpm_db_models

COMPARISON_TYPE = 'rpmdiff'

database.Base.metadata.create_all(database.engine())

session = database.session()
if session.query(database.ComparisonType).filter_by(
        name=COMPARISON_TYPE
).one_or_none() is None:
    session.add(database.ComparisonType(name=COMPARISON_TYPE))
    session.commit()
