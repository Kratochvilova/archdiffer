# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 11:58:24 2017

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from .flask_app import flask_app
from ..repository import load_plugins_flask_frontends
from . import common_tasks, database_tasks

load_plugins_flask_frontends()
