# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Tue Apr 18 11:58:24 2017

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from .celery_app import celery_app
from ..repository import load_plugins_workers

load_plugins_workers()
