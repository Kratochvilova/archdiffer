# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Mon Jul 17 21:49:00 2017

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from . import celery_app

celery_app.start()
