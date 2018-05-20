# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Sun May 20 15:15:08 2018

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from flask import request, flash, redirect, url_for, g
from flask import session as flask_session
from flask_openid import OpenID
from .flask_app import flask_app
from .common_views import my_render_template
from ..database import User

oid = OpenID(flask_app, safe_roots=[])

@flask_app.before_request
def lookup_current_user():
    g.user = None
    if 'openid' in flask_session:
        openid = flask_session['openid']
        g.user = User.query(g.db_session, openid=openid)

def form_openid_url(url, username):
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
                openid_url = form_openid_url(
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
        flash('Successfully signed in.', 'success')
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
            flash('You have to provide username.', 'danger')
        else:
            g.user = User.add(
                g.db_session, flask_session['openid'], username
            )
            if g.user is None:
                flash('Username already exists.', 'danger')
            else:
                flash('Profile successfully created.', 'success')
            return redirect(oid.get_next_url())
    return my_render_template('create_profile.html', next=oid.get_next_url())

@flask_app.route('/logout')
def logout():
    """Logout user."""
    flask_session.pop('openid', None)
    g.user = None
    flash('You were signed out.', 'success')
    return redirect(oid.get_next_url())
