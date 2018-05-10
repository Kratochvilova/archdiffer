# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Mon Jul 17 10:23:02 2017

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

import importlib
import os

workers = {}
flask_frontends = {}

def load_plugins_workers():
    """Load worker plugins from all plugins if possible."""
    for name in os.listdir(os.path.join(os.path.dirname(__file__), 'plugins')):
        try:
            workers[name] = importlib.import_module(
                '.plugins.' + name + '.worker', 'archdiffer'
            )
        except ImportError as ie:
            print(ie)

def load_plugins_flask_frontends():
    """Load flask-frontend plugins from all plugins if possible."""
    for name in os.listdir(os.path.join(os.path.dirname(__file__), 'plugins')):
        try:
            flask_frontends[name] = importlib.import_module(
                '.plugins.' + name + '.flask_frontend', 'archdiffer'
            )
        except ImportError as ie:
            print(ie)
