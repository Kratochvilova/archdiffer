# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 12:09:08 2017

@author: pavla
"""

from flask import (Blueprint, render_template, abort, request, session, g,
flash, redirect, url_for)
from celery import Celery
from ... import database
from ...repository import register_blueprint

celery_app = Celery(broker='pyamqp://localhost', )


MODULE = 'zip'

bp_zipdiff = Blueprint('zipdiff', __name__, template_folder='templates')
register_blueprint('zipdiff', bp_zipdiff)
bp_zipdiff.config = {}

@bp_zipdiff.record
def record_params(setup_state):
    """Overwriting record_params only to keep app.config.
    """
    app = setup_state.app
    bp_zipdiff.config = dict(
        [(key,value) for (key,value) in app.config.items()]
    )

@bp_zipdiff.before_request
def before_request():
    g.session = database.Session()

@bp_zipdiff.teardown_request
def teardown_request(exception):
    session = getattr(g, 'session', None)
    if session is not None:
        try:
            session.commit()
        except:
            pass
        finally:
            session.close()

@bp_zipdiff.route('/')
def show_comparisons():
    dicts = []
    comps = g.session.query(database.Comparison)
    for instance in comps.order_by(database.Comparison.id):
        dicts.append(instance.get_dict())
    return render_template('show_comparisons.html', comparisons=dicts)

@bp_zipdiff.route('/comparison/<int:comp_id>')
def show_differences(comp_id):
    dicts = []
    diffs = g.session.query(database.Difference).filter_by(id_comp=comp_id)
    for instance in diffs.order_by(database.Difference.id):
        dicts.append(instance.get_dict())
    return render_template('show_differences.html', differences=dicts)

@bp_zipdiff.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    celery_app.send_task(
        'zipdiff.compare', args=(request.form['zip1'], request.form['zip2'])
    )
    flash('New entry was successfully posted')
    return redirect(url_for('zipdiff.show_comparisons'))
