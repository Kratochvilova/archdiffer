# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 10:36:51 2017

@author: pavla
"""

from flask import Flask
from .config import FlaskConfig

flask_app = Flask(__name__)
flask_app.config.from_object(FlaskConfig)
