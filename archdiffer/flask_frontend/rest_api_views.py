# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Sun May 20 15:41:14 2018

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

import base64
import datetime
import functools
from flask import request, redirect, url_for, g, abort
from .flask_app import flask_app
from .exceptions import AuthFailed
from .common_views import my_render_template
from ..database import User

def rest_api_auth_required(f):
    """Checks REST API authentization."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        api_login = None
        try:
            if "Authorization" in request.headers:
                base64string = request.headers["Authorization"]
                base64string = base64string.split()[1].strip()
                userstring = base64.b64decode(base64string)
                (api_login, token) = userstring.decode("utf-8").split(":")
        except Exception:
            api_login = token = None
        token_auth = False
        if token and api_login:
            user = User.query(g.db_session, api_login=api_login)
            if (user and user.api_token == token and
                    user.api_token_expiration >= datetime.date.today()):
                token_auth = True
                g.user = user
        if not token_auth:
            message = ("Login invalid/expired. Renew your REST API token.")
            raise AuthFailed(message)
        return f(*args, **kwargs)
    return decorated_function

@flask_app.route('/api')
def show_rest_api():
    """Show page for api."""
    return my_render_template('show_rest_api.html')

@flask_app.route('/generate_token', methods=['POST'])
def generate_token():
    """Generate new login and token for REST API."""
    if g.get('user', None) is None:
        abort(401)

    g.user.new_token(
        g.db_session,
        size=flask_app.config['API_TOKEN_LENGTH'],
        token_expiration=flask_app.config['API_TOKEN_EXPIRATION'],
    )

    return redirect(url_for('show_rest_api'))
