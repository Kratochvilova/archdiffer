# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 14:55:56 2017

@author: pavla
"""

import base64
import random
import string
import datetime
import functools
from flask import render_template, request, flash, redirect, url_for, g, abort
from flask import session as flask_session
from flask_openid import OpenID
from .flask_app import flask_app
from .exceptions import AuthFailed
from ..database import session as db_session
from ..database import ComparisonType, User

oid = OpenID(flask_app, safe_roots=[])

def my_render_template(html, **arguments):
    """Call render_template with comparison_types as one of the arguments.

    :param string html: name of the template
    :param **arguments: other arguments to be passed while rendering template
    """
    arguments.setdefault(
        'comparison_types', ComparisonType.get_cache(g.db_session)
    )
    return render_template(html, **arguments)

@flask_app.before_request
def new_database_session():
    """Get new database session for each request."""
    g.db_session = db_session()

@flask_app.teardown_request
def close_database_session(exception):
    """Commit and close database session at the end of request."""
    ses = getattr(g, 'db_session', None)
    if ses is not None:
        try:
            ses.commit()
        except:
            pass
        finally:
            ses.close()

@flask_app.before_request
def lookup_current_user():
    g.user = None
    if 'openid' in flask_session:
        openid = flask_session['openid']
        g.user = User.query(g.db_session, openid=openid)

def get_openid_url(url, username):
    """Fill in username into url."""
    return url.replace('<username>', username)

@flask_app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    """Login user."""
    if g.get('user', None) is not None:
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid_url = ''
        provider = request.form.get('provider')
        if provider:
            username = request.form.get('username')
            if username:
                openid_url = get_openid_url(
                    flask_app.config['OPENID_PROVIDERS'][provider], username
                )
        else:
            openid_url = request.form.get('openid')
        if openid_url:
            return oid.try_login(openid_url, ask_for=['nickname'])
    return my_render_template(
        'login.html',
        next=oid.get_next_url(),
        error=oid.fetch_error(),
        providers=flask_app.config['OPENID_PROVIDERS'].keys()
    )

@oid.after_login
def create_or_login(resp):
    """Check if user exists and finish login or redirect to create_profile."""
    flask_session['openid'] = resp.identity_url
    user = User.query(g.db_session, openid=resp.identity_url)
    if user is not None:
        flash(u'Successfully signed in')
        g.user = user
        return redirect(oid.get_next_url())
    return redirect(
        url_for(
            'create_profile', next=oid.get_next_url(), username=resp.nickname
        )
    )

@flask_app.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    """Add new user."""
    if g.get('user', None) is not None or 'openid' not in flask_session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        if not username:
            flash(u'Error: you have to provide username')
        else:
            g.user = User.add(
                g.db_session, flask_session['openid'], username
            )
            if g.user is None:
                flash(u'Error: username already exists')
            else:
                flash(u'Profile successfully created')
            return redirect(oid.get_next_url())
    return my_render_template('create_profile.html', next=oid.get_next_url())

@flask_app.route('/logout')
def logout():
    """Logout user."""
    flask_session.pop('openid', None)
    g.user = None
    flash(u'You were signed out')
    return redirect(oid.get_next_url())

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

def generate_api_token(size=30):
    """Generate a random string used as login or token for REST API.

    :param int size: the size of the token to generate, defaults to 30 chars
    :return string: the API token for the user
    """
    return ''.join(random.choice(string.ascii_lowercase) for x in range(size))

@flask_app.route('/generate_token', methods=['POST'])
def generate_token():
    """Generate new login and token for REST API."""
    if g.get('user', None) is None:
        abort(401)

    g.user.api_login = generate_api_token(flask_app.config["API_TOKEN_LENGTH"])
    g.user.api_token = generate_api_token(flask_app.config["API_TOKEN_LENGTH"])
    g.user.api_token_expiration = datetime.date.today() + datetime.timedelta(
        days=flask_app.config["API_TOKEN_EXPIRATION"]
    )
    g.db_session.add(g.user)
    g.db_session.commit()

    return redirect(url_for('show_rest_api'))
