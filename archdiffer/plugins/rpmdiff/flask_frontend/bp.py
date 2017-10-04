# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 22:54:57 2017

@author: pavla
"""

from flask import (Blueprint, render_template, abort, request, session, g,
flash, redirect, url_for)
from celery import Celery
from .... import database
from .. import rpm_db_models

celery_app = Celery(broker='pyamqp://localhost', )

MODULE = 'rpm'

bp = Blueprint('rpmdiff', __name__, template_folder='templates')
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
    g.session = database.session()

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
    comps = g.session.query(rpm_db_models.RPMComparison)
    for instance in comps.order_by(rpm_db_models.RPMComparison.id_comp):
        dicts.append(instance.get_dict())
    return render_template('rpm_show_comparisons.html', comparisons=dicts)

@bp.route('/comparison/<int:id_comp>')
def show_differences(id_comp):
    dicts = []
    diffs = g.session.query(rpm_db_models.RPMDifference).filter_by(id_comp=id_comp)
    for instance in diffs.order_by(rpm_db_models.RPMDifference.id_comp):
        dicts.append(instance.get_dict())
    return render_template('rpm_show_differences.html', differences=dicts)

@bp.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    pkg1 = {
        'name': request.form['name1'],
        'arch': request.form['arch1'],
        'epoch': request.form['epoch1'],
        'version': request.form['version1'],
        'release': request.form['release1'],
        'repository': request.form['repo1']
    }
    pkg2 = {
       'name': request.form['name2'],
        'arch': request.form['arch2'],
        'epoch': request.form['epoch2'],
        'version': request.form['version2'],
        'release': request.form['release2'],
        'repository': request.form['repo2']
    }
    celery_app.send_task(
        'rpmdiff.compare', args=(pkg1, pkg2)
    )
    flash('New entry was successfully posted')
    return redirect(url_for('rpmdiff.show_comparisons'))
