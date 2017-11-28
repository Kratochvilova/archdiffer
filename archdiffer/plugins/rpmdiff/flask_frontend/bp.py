# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 22:54:57 2017

@author: pavla
"""

from flask import Blueprint, abort, request, g, flash, redirect, url_for
from flask import session as flask_session
from celery import Celery
from ..rpm_db_models import (RPMComparison, RPMDifference, RPMPackage,
                             RPMRepository)
from ....flask_frontend.common_tasks import my_render_template

celery_app = Celery(broker='pyamqp://localhost', )

COMPARISON_TYPE = 'rpmdiff'

bp = Blueprint(COMPARISON_TYPE, __name__, template_folder='templates')
bp.config = {}

@bp.record
def record_params(setup_state):
    """Overwrite record_params only to keep app.config."""
    app = setup_state.app
    bp.config = dict(
        [(key, value) for (key, value) in app.config.items()]
    )

@bp.route('/')
def show_comparisons():
    comps = g.db_session.query(RPMComparison)
    return my_render_template('rpm_show_comparisons.html', comparisons=comps)

@bp.route('/comparison/<int:id_comp>')
def show_differences(id_comp):
    comp = g.db_session.query(RPMComparison).filter_by(id_comp=id_comp).one()
    diffs = g.db_session.query(RPMDifference).filter_by(id_comp=id_comp).all()
    return my_render_template(
        'rpm_show_differences.html',
        comp=comp,
        differences=diffs
    )

@bp.route('/package/<int:pkg_id>')
def show_package(pkg_id):
    pkg = g.db_session.query(RPMPackage).filter_by(id=pkg_id).one()
    return my_render_template('rpm_show_package.html', pkg=pkg)

@bp.route('/repository/<int:repo_id>')
def show_repository(repo_id):
    repo = g.db_session.query(RPMRepository).filter_by(id=repo_id).one()
    return my_render_template('rpm_show_repository.html', repo=repo)

@bp.route('/packages')
def show_packages():
    pkgs = g.db_session.query(RPMPackage).all()
    return my_render_template('rpm_show_packages.html', pkgs=pkgs)

@bp.route('/repositories')
def show_repositories():
    repos = g.db_session.query(RPMRepository).all()
    return my_render_template('rpm_show_repositories.html', repos=repos)

@bp.route('/add', methods=['POST'])
def add_entry():
    if not flask_session.get('logged_in'):
        abort(401)
    pkg1 = {
        'name': request.form['name1'],
        'arch': request.form['arch1'],
        'epoch': request.form['epoch1'],
        'version': request.form['version1'],
        'release': request.form['release1'],
        'repository': request.form['repo1'],
    }
    pkg2 = {
        'name': request.form['name2'],
        'arch': request.form['arch2'],
        'epoch': request.form['epoch2'],
        'version': request.form['version2'],
        'release': request.form['release2'],
        'repository': request.form['repo2'],
    }
    celery_app.send_task(
        'rpmdiff.compare', args=(pkg1, pkg2)
    )
    flash('New entry was successfully posted')
    return redirect(url_for('rpmdiff.show_comparisons'))
