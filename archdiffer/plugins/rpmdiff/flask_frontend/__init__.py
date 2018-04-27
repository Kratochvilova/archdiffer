# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Sat Sep 16 22:54:38 2017

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from .bp import bp
from ....flask_frontend.flask_app import flask_app

flask_app.register_blueprint(bp, url_prefix='/'+'rpmdiff')
