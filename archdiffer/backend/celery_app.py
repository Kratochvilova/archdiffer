# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Fri Sep  1 10:22:37 2017

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from celery import Celery

celery_app = Celery('backend', broker='pyamqp://localhost')
