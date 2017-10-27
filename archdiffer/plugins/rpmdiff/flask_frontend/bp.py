# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 22:54:57 2017

@author: pavla
"""

from flask import (Blueprint, render_template, abort, request, session, g,
flash, redirect, url_for)
from celery import Celery
from .... import database
from ..rpm_db_models import (RPMComparison, RPMDifference, RPMPackage,
RPMRepository)

celery_app = Celery(broker='pyamqp://localhost', )

MODULE = 'rpm'

bp = Blueprint('rpmdiff', __name__, template_folder='templates')
bp.config = {}

@bp.record
def record_params(setup_state):
    """Overwrite record_params only to keep app.config."""
    app = setup_state.app
    bp.config = dict(
        [(key,value) for (key,value) in app.config.items()]
    )

@bp.route('/')
def show_comparisons():
    dicts = []
    comps = g.session.query(RPMComparison)
    for instance in comps.order_by(RPMComparison.id_comp):
        comparison_dict = instance.get_dict()
        pkg1 = g.session.query(RPMPackage).filter_by(id=instance.pkg1_id).one()
        pkg2 = g.session.query(RPMPackage).filter_by(id=instance.pkg2_id).one()
        comparison_dict['pkg1_name'] = pkg1.name
        comparison_dict['pkg2_name'] = pkg2.name
        dicts.append(comparison_dict)        
    return render_template('rpm_show_comparisons.html', comparisons=dicts)

@bp.route('/comparison/<int:id_comp>')
def show_differences(id_comp):
    dicts = []
    diffs = g.session.query(RPMDifference).filter_by(id_comp=id_comp)
    for instance in diffs.order_by(RPMDifference.id_comp):
        dicts.append(instance.get_dict())
    return render_template('rpm_show_differences.html', differences=dicts)

@bp.route('/package/<int:pkg_id>')
def show_package(pkg_id):
    pkg = g.session.query(RPMPackage).filter_by(id=pkg_id).one()
    package_dict = pkg.get_dict()
    repo = g.session.query(RPMRepository).filter_by(id=pkg.id_repo).one()
    package_dict['repo_path'] = repo.path
    return render_template('rpm_show_package.html', pkg=package_dict)

@bp.route('/repository/<int:repo_id>')
def show_repository(repo_id):
    repo = g.session.query(RPMRepository).filter_by(id=repo_id).one()
    return render_template('rpm_show_repository.html', repo=repo.get_dict())


@bp.route('/packages')
def show_packages():
    dicts = []
    pkgs = g.session.query(RPMPackage).all()
    for pkg in pkgs:
        package_dict = pkg.get_dict()
        repo = g.session.query(RPMRepository).filter_by(id=pkg.id_repo).one()
        package_dict['repo_path'] = repo.path
        dicts.append(package_dict)
    return render_template('rpm_show_packages.html', pkgs=dicts)

@bp.route('/repositories')
def show_repositories():
    dicts = []
    repos = g.session.query(RPMRepository).all()
    for repo in repos:
        dicts.append(repo.get_dict())
    return render_template('rpm_show_repositories.html', repos=dicts)


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
