# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Wed May  2 15:58:28 2018

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from ...backend.celery_app import celery_app

# Celery task registered in celery app. The name should be unique - you can for
# example use plugin name as prefix.
@celery_app.task(name='example_plugin.example_task')
def example_task():
    """Example celery task."""
    pass
