# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 11:58:24 2017

@author: pavla
"""

from flask import Flask
from ..repository import import_plugins, blueprints

import_plugins()

app = Flask(__name__)

# TODO: change so that I can use my own config and not flask config
app.config.from_pyfile('config.py')


for key, blueprint in blueprints.items():
    app.register_blueprint(blueprint, url_prefix='/'+key)
