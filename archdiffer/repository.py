# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 10:23:02 2017

@author: pavla
"""

import importlib
import os

plugins = {}
comparators = {}
blueprints = {}

def import_plugins():
    for name in os.listdir(os.path.join(os.path.dirname(__file__), 'plugins')):
        plugins[name] = importlib.import_module(
            '.plugins.' + name, 'archdiffer'
        )

def register_comparator(comparator_name, comparator):
    comparators[comparator_name] = comparator

def register_blueprint(plugin_name, blueprint):
    blueprints[plugin_name] = blueprint
