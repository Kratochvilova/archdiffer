# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 10:23:02 2017

@author: pavla
"""

# TODO: make this so that plugins register their services (not every plugin
#       needs to do the comparison, and there may be several comparison types
#       within one plugin)

import importlib
import os
from .config import PLUGINS_PATH

repository = {}

for name in os.listdir(PLUGINS_PATH):
    key = name.rsplit('.', 1)[0]
    repository[key] = importlib.import_module(
        '.plugins.' + key, 'archdiffer.backend'
    )
