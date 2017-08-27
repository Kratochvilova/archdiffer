# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 11:58:24 2017

@author: pavla
"""

from celery import Celery
from ..repository import import_plugins
from .resolve_type import resolve_type

import_plugins()

celery_app = Celery('backend', broker='pyamqp://localhost')

@celery_app.task(name='compare')
def compare(comparator, pkg1, pkg2):
    resolve_type(comparator, pkg1, pkg2)
