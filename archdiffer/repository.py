# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 10:23:02 2017

@author: pavla
"""

import importlib
import os

plugins = {}
workers = {}
flask_frontends = {}
blueprints = {}

def import_plugins():
    for name in os.listdir(os.path.join(os.path.dirname(__file__), 'plugins')):
        plugins[name] = importlib.import_module(
            '.plugins.' + name, 'archdiffer'
        )

def import_workers():
    for name in os.listdir(os.path.join(os.path.dirname(__file__), 'plugins')):
        try:
            workers[name] = importlib.import_module(
                '.plugins.' + name + '.worker', 'archdiffer'
            )
        except:
            pass

def import_flask_frontends():
    for name in os.listdir(os.path.join(os.path.dirname(__file__), 'plugins')):
        try:
            flask_frontends[name] = importlib.import_module(
                '.plugins.' + name + '.flask_frontend', 'archdiffer'
            )
        except:
            pass

def register_blueprint(plugin_name, blueprint):
    blueprints[plugin_name] = blueprint
