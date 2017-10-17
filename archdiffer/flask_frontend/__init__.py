# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 11:58:24 2017

@author: pavla
"""

from .flask_app import flask_app
from ..repository import load_plugins_flask_frontends
from . import common_tasks

load_plugins_flask_frontends()
