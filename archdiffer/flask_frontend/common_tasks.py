# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 14:55:56 2017

@author: pavla
"""

from flask import (render_template, request, session, flash, redirect, url_for,
g)
from .flask_app import flask_app
from .. import database

@flask_app.before_request
def before_request():
    """Get new database session for each request."""
    g.session = database.session()

@flask_app.teardown_request
def teardown_request(exception):
    """Commit and close database session at the end of request."""
    session = getattr(g, 'session', None)
    if session is not None:
        try:
            session.commit()
        except:
            pass
        finally:
            session.close()

@flask_app.route('/')
def index():
    dicts = []
    comps = g.session.query(database.Comparison)
    for instance in comps.order_by(database.Comparison.id):
        dicts.append(instance.get_dict())
    return render_template('show_comparisons.html', comparisons=dicts)

@flask_app.route('/plugins')
def show_plugins():
    plugins_list = []
    plugins = g.session.query(database.Plugin)
    for instance in plugins.order_by(database.Plugin.id):
        plugins_list.append(instance.plugin)
    return render_template('show_plugins.html', plugins=plugins_list)

@flask_app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != flask_app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != flask_app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@flask_app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))

