# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 11:58:24 2017

@author: pavla
"""

from flask import Flask
from ..repository import import_plugins, blueprints
from .config import FlaskConfig

import_plugins()

app = Flask(__name__)

app.config.from_object(FlaskConfig)

for key, blueprint in blueprints.items():
    app.register_blueprint(blueprint, url_prefix='/'+key)
