# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 11:58:24 2017

@author: pavla
"""

from celery import Celery
from .resolve_type import resolve_type

celery_app = Celery('backend', broker='pyamqp://localhost')

@celery_app.task(name='compare')
def compare(compare_type, pkg1, pkg2):
    resolve_type(compare_type, pkg1, pkg2)
