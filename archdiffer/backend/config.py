# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 22:18:26 2017

@author: pavla
"""

import os
import os.path

BACKEND_PATH = os.path.dirname(os.path.abspath(__file__))
PLUGINS_PATH = os.path.join(BACKEND_PATH, 'plugins')
EXAMPLES_PATH = os.path.join(BACKEND_PATH, 'test_examples')

DATABASE = '/var/lib/archdiffer/database.db'