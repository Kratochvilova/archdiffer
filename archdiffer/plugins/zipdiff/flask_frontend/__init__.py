# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 11:15:44 2017

@author: pavla
"""

from .bp import bp
from ....flask_frontend.flask_app import flask_app

flask_app.register_blueprint(bp, url_prefix='/'+'zipdiff')
