# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 11:58:24 2017

@author: pavla
"""

from worker.zipdiff import zipdiff
from archdiffer import database
from worker.config import DATABASE

def run():
    db = database.DatabaseConnection(DATABASE)
    zipdiff.process_requests(db)
    db.print_all()
