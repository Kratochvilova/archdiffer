# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 11:58:24 2017

@author: pavla
"""

from celery import Celery
import os
from .config import PLUGINS_PATH

plugins = []
for name in os.listdir(PLUGINS_PATH):
    key = name.rsplit('.', 1)[0]
    plugins.append('worker.plugins.' + key)
    
app = Celery('foo', broker='pyamqp://localhost')

@app.task(name='compare')
def compare(x, y):
    print("compare")
    return x - y

#from worker.zipdiff import zipdiff
#from archdiffer import database
#from worker.config import DATABASE

#def run():
#    db = database.DatabaseConnection(DATABASE)
#    zipdiff.process_requests(db)
#    db.print_all()
