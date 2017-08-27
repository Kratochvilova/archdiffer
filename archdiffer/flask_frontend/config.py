# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 22:18:26 2017

@author: pavla
"""

from ..config import config

class FlaskConfig(object):
    DEBUG = config['web']['DEBUG']
    SECRET_KEY = config['web']['SECRET_KEY']
    USERNAME = config['web']['USERNAME']
    PASSWORD = config['web']['PASSWORD']
