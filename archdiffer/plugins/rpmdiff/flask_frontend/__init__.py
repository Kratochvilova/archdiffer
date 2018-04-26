# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 22:54:38 2017

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from .bp import bp
from ....flask_frontend.flask_app import flask_app

flask_app.register_blueprint(bp, url_prefix='/'+'rpmdiff')
