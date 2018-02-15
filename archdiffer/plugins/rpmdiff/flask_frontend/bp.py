# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 22:54:57 2017

@author: pavla
"""

from flask import Blueprint, abort, request, g, flash, redirect, url_for
from flask import session as flask_session
from flask_restful import Api, Resource, fields, marshal_with
from celery import Celery
from ..rpm_db_models import (RPMComparison, RPMDifference, RPMPackage,
                             RPMRepository)
from .. import constants
from .database_functions import (COMPARISON_TYPE, joined_query,
                                 iter_query_result)
from ....flask_frontend.common_tasks import my_render_template
from ....flask_frontend.database_tasks import (query_database_table,
                                               modify_query_by_request)

celery_app = Celery(broker='pyamqp://localhost', )

bp = Blueprint(COMPARISON_TYPE, __name__, template_folder='templates')
bp.config = {}
flask_api = Api(bp)

@bp.context_processor
def inject_constants():
    return vars(constants)

@bp.record
def record_params(setup_state):
    """Overwrite record_params only to keep app.config."""
    app = setup_state.app
    bp.config = dict(
        [(key, value) for (key, value) in app.config.items()]
    )

@bp.route('/')
def show_comparisons():
    comps = dict(iter_query_result(joined_query()))
    return my_render_template('rpm_show_comparisons.html', comparisons=comps)

@bp.route('/comparison/<int:id_comp>')
def show_differences(id_comp):
    query = joined_query(RPMDifference).filter(RPMComparison.id_comp==id_comp)
    comparison = dict(iter_query_result(query, RPMDifference))
    return my_render_template(
        'rpm_show_differences.html',
        comparison=comparison
    )

@bp.route('/package/<int:pkg_id>')
def show_package(pkg_id):
    query = joined_query(RPMPackage).filter(RPMPackage.id==pkg_id)
    pkg = dict(iter_query_result(query, RPMPackage))
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
    if 'openid' not in flask_session:
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

# Marshalling sqlalchemy objects
class StateItem(fields.Raw):
    def format(self, value):
        return constants.STATE_STRINGS[value]

class CategoryItem(fields.Raw):
    def format(self, value):
        return constants.CATEGORY_STRINGS[value]

class DiffTypeItem(fields.Raw):
    def format(self, value):
        return constants.DIFF_TYPE_STRINGS[value]

RPM_COMPARISON_FIELDS = {
    'id_comp': fields.Integer,
    'pkg1_id': fields.Integer,
    'pkg2_id': fields.Integer,
    'state': StateItem,
}

RPM_DIFFERENCE_FIELDS = {
    'id': fields.Integer,
    'id_comp': fields.Integer,
    'category': CategoryItem,
    'diff_type': DiffTypeItem,
    'diff_info': fields.String,
    'diff': fields.String,
}

RPM_PACKAGE_FIELDS = {
    'id': fields.Integer,
    'name': fields.String,
    'arch': fields.String,
    'epoch': fields.String,
    'version': fields.String,
    'release': fields.String,
    'id_repo': fields.Integer,
}

RPM_REPOSITORY_FIELDS = {
    'id': fields.Integer,
    'path': fields.String,
}

# Resources
class ShowRPMComparisons(Resource):
    @marshal_with(RPM_COMPARISON_FIELDS)
    def get(self):
        return query_database_table(RPMComparison)

class ShowRPMDifferences(Resource):
    @marshal_with(RPM_DIFFERENCE_FIELDS)
    def get(self):
        return query_database_table(RPMDifference)

class ShowRPMPackages(Resource):
    @marshal_with(RPM_PACKAGE_FIELDS)
    def get(self):
        return query_database_table(RPMPackage)

class ShowRPMRepositories(Resource):
    @marshal_with(RPM_REPOSITORY_FIELDS)
    def get(self):
        return query_database_table(RPMRepository)

flask_api.add_resource(ShowRPMComparisons, '/rest/comparisons')
flask_api.add_resource(ShowRPMDifferences, '/rest/differences')
flask_api.add_resource(ShowRPMPackages, '/rest/packages')
flask_api.add_resource(ShowRPMRepositories, '/rest/repositories')

class ShowJoinedData(Resource):    
    def get(self):
        return dict(iter_query_result(modify_query_by_request(
            joined_query(RPMDifference)), RPMDifference
        ))

flask_api.add_resource(ShowJoinedData, '/rest/joined')
