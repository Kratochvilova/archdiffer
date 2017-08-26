# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 11:58:24 2017

@author: pavla
"""

from flask import Flask
from .zipdiff.zipdiff import bp_zipdiff

app = Flask(__name__)

# TODO: change so that I can use my own config and not flask config
app.config.from_pyfile('config.py')

app.register_blueprint(bp_zipdiff, url_prefix='/zipdiff')

