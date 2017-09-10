# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 11:09:49 2017

@author: pavla
"""

from flask import (Blueprint, render_template, abort, request, session, g,
flash, redirect, url_for)
from celery import Celery
from .... import database

celery_app = Celery(broker='pyamqp://localhost', )

MODULE = 'zip'

bp = Blueprint('zipdiff', __name__, template_folder='templates')
bp.config = {}

@bp.record
def record_params(setup_state):
    """Overwriting record_params only to keep app.config.
    """
    app = setup_state.app
    bp.config = dict(
        [(key,value) for (key,value) in app.config.items()]
    )

@bp.before_request
def before_request():
    g.session = database.Session()

@bp.teardown_request
def teardown_request(exception):
    session = getattr(g, 'session', None)
    if session is not None:
        try:
            session.commit()
        except:
            pass
        finally:
            session.close()

@bp.route('/')
def show_comparisons():
    dicts = []
    comps = g.session.query(database.Comparison)
    for instance in comps.order_by(database.Comparison.id):
        dicts.append(instance.get_dict())
    return render_template('show_comparisons.html', comparisons=dicts)

@bp.route('/comparison/<int:comp_id>')
def show_differences(comp_id):
    dicts = []
    diffs = g.session.query(database.Difference).filter_by(id_comp=comp_id)
    for instance in diffs.order_by(database.Difference.id):
        dicts.append(instance.get_dict())
    return render_template('show_differences.html', differences=dicts)

@bp.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    celery_app.send_task(
        'zipdiff.compare', args=(request.form['zip1'], request.form['zip2'])
    )
    flash('New entry was successfully posted')
    return redirect(url_for('zipdiff.show_comparisons'))
