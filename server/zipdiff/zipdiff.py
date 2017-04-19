# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 12:09:08 2017

@author: pavla
"""

from flask import Blueprint, render_template, abort, request, session, g, flash, redirect, url_for
from jinja2 import TemplateNotFound
from archdiffer import database

MODULE = 'zip'

bp_zipdiff = Blueprint('zipdiff', __name__, template_folder='templates')
bp_zipdiff.config = {}

@bp_zipdiff.record
def record_params(setup_state):
  app = setup_state.app
  bp_zipdiff.config = dict([(key,value) for (key,value) in app.config.items()])

@bp_zipdiff.before_request
def before_request():
    g.db = database.DatabaseConnection(bp_zipdiff.config['DATABASE'])

@bp_zipdiff.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.con.close()

@bp_zipdiff.route('/')
def show_comparisons():
    rows = g.db.get_table('comparisons')
    dicts = []
    for row in rows:
        dicts.append(g.db.parse_row_comparisons(row))
    print(dicts)
    return render_template('show_comparisons.html', comparisons=dicts)

@bp_zipdiff.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.add_request(MODULE, request.form['zip1'], request.form['zip2'])
    flash('New entry was successfully posted')
    return redirect(url_for('zipdiff.show_comparisons'))

@bp_zipdiff.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != bp_zipdiff.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != bp_zipdiff.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('zipdiff.show_comparisons'))
    return render_template('login.html', error=error)

@bp_zipdiff.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('zipdiff.show_comparisons'))
