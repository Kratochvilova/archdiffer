# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 11:58:24 2017

@author: pavla
"""

from flask import Flask
from ..repository import import_flask_frontends, blueprints
from .config import FlaskConfig

import_flask_frontends()

app = Flask(__name__)

app.config.from_object(FlaskConfig)

for key, blueprint in blueprints.items():
    app.register_blueprint(blueprint, url_prefix='/'+key)

from . import login_tasks
