# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 14:55:56 2017

@author: pavla
"""

from flask import render_template, request, session, flash, redirect, url_for
from .flask_app import flask_app

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
            return redirect(url_for('zipdiff.show_comparisons'))
    return render_template('login.html', error=error)

@flask_app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('zipdiff.show_comparisons'))

