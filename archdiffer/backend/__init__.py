# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 11:58:24 2017

@author: pavla
"""

from .celery_app import celery_app
from ..repository import load_plugins_workers

load_plugins_workers()
