# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 10:22:37 2017

@author: pavla
"""

from celery import Celery

celery_app = Celery('backend', broker='pyamqp://localhost')
