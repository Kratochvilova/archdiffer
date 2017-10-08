# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 10:23:02 2017

@author: pavla
"""

import importlib
import os

workers = {}
flask_frontends = {}

def load_plugins_workers():
    """Load worker modules from all plugins if possible."""
    for name in os.listdir(os.path.join(os.path.dirname(__file__), 'plugins')):
        try:
            workers[name] = importlib.import_module(
                '.plugins.' + name + '.worker', 'archdiffer'
            )
        except:
            pass

def load_plugins_flask_frontends():
    """Load flask-frontend modules from all plugins if possible."""
    for name in os.listdir(os.path.join(os.path.dirname(__file__), 'plugins')):
        try:
            flask_frontends[name] = importlib.import_module(
                '.plugins.' + name + '.flask_frontend', 'archdiffer'
            )
        except:
            pass
