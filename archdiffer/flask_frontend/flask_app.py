# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Sun Sep 10 10:36:51 2017

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from flask import Flask
from flask_restful import Api
from .config import FlaskConfig

flask_app = Flask(__name__)
flask_app.config.from_object(FlaskConfig)
flask_api = Api(flask_app)
