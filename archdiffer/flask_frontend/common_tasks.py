# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 14:55:56 2017

@author: pavla
"""

from flask import render_template, request, flash, redirect, url_for, g
from flask import session as flask_session
from flask_openid import OpenID
from .flask_app import flask_app
from ..database import session as db_session
from ..database import ComparisonType, User

oid = OpenID(flask_app, safe_roots=[])

def get_comparison_types():
    """Get all comparison types from the database.

    :return sqlalchemy.orm.query.Query: resulting query
    """
    ses = db_session()
    comp_types = ComparisonType.query(ses)
    ses.close()
    return comp_types

comparison_types = get_comparison_types()

def my_render_template(html, **arguments):
    """Call render_template with comparison_types as one of the arguments.

    :param string html: name of the template
    :param **arguments: other arguments to be passed while rendering template
    """
    arguments.setdefault('comparison_types', comparison_types)
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
        g.user = User.query_by_openid(g.db_session, openid)

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
        providers = flask_app.config['OPENID_PROVIDERS'].keys()
    )

@oid.after_login
def create_or_login(resp):
    """Check if user exists and finish login or redirect to create_profile."""
    flask_session['openid'] = resp.identity_url
    user = User.query_by_openid(g.db_session, resp.identity_url)
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
    return render_template('create_profile.html', next=oid.get_next_url())

@flask_app.route('/logout')
def logout():
    """Logout user."""
    flask_session.pop('openid', None)
    g.user = None
    flash(u'You were signed out')
    return redirect(oid.get_next_url())
