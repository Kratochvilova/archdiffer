# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 22:54:57 2017

@author: pavla
"""

from flask import Blueprint, abort, request, flash, redirect, url_for, g
from flask import session as flask_session
from flask_restful import Api, Resource
from celery import Celery
from ..rpm_db_models import (RPMComparison, RPMDifference, RPMPackage,
                             RPMRepository, iter_query_result)
from .. import constants
from ....database import Comparison, ComparisonType, modify_query
from ....flask_frontend.common_tasks import my_render_template
from ....flask_frontend.request_parser import parse_request
from ....flask_frontend.database_tasks import get_pagination_modifiers

celery_app = Celery(broker='pyamqp://localhost', )

bp = Blueprint(
    constants.COMPARISON_TYPE, __name__, template_folder='templates'
)
bp.config = {}
flask_api = Api(bp)

@bp.context_processor
def inject_constants():
    """Add all constants from constants module to the tamplate context."""
    return vars(constants)

@bp.record
def record_params(setup_state):
    """Overwrite record_params only to keep app.config."""
    app = setup_state.app
    bp.config = dict(
        [(key, value) for (key, value) in app.config.items()]
    )

@bp.route('/')
def index():
    """Show index page."""
    modifiers = get_pagination_modifiers()
    query = RPMComparison.comparisons_query(g.db_session, modifiers)
    comps = dict(iter_query_result(query, Comparison))
    items_count = RPMComparison.comparisons_count(g.db_session)
    return my_render_template(
        'rpm_show_index.html', 
        comparisons=comps,
        items_count=items_count,
        limit=modifiers['limit'],
        offset=modifiers['offset'],
        endpoint='rpmdiff.index',
        arguments={},
    )

@bp.route('/comparisons')
def show_comparisons():
    """Show all comparisons."""
    modifiers = get_pagination_modifiers()
    query = RPMComparison.comparisons_query(g.db_session, modifiers)
    comps = dict(iter_query_result(query, Comparison))
    items_count = RPMComparison.comparisons_count(g.db_session)
    return my_render_template(
        'rpm_show_comparisons.html',
        comparisons=comps,
        items_count=items_count,
        limit=modifiers['limit'],
        offset=modifiers['offset'],
        endpoint='rpmdiff.show_comparisons',
        arguments={},
    )

@bp.route('/new')
def show_new_comparison_form():
    """Show form for new comparison."""
    return my_render_template('rpm_show_new_comparison_form.html')

@bp.route('/groups/<int:id_group>')
def show_group(id_group):
    """Show rpm comparisons in given group.
    
    :param int id_group: id of the group
    """
    modifiers = get_pagination_modifiers()
    query = RPMComparison.comparisons_query(g.db_session)
    query = query.filter(
        ComparisonType.name == constants.COMPARISON_TYPE,
        Comparison.id == id_group,
    )
    comps = dict(iter_query_result(query, Comparison))
    return my_render_template(
        'rpm_show_groups.html',
        comparisons=comps,
        items_count=1,
        limit=modifiers['limit'],
        offset=modifiers['offset'],
        endpoint='rpmdiff.show_group',
        arguments={},
    )

@bp.route('/groups')
def show_groups():
    """Show all rpm comparisons."""
    modifiers = get_pagination_modifiers()
    query = RPMComparison.comparisons_query(g.db_session, modifiers)
    query = query.filter(ComparisonType.name == constants.COMPARISON_TYPE)
    comps = dict(iter_query_result(query, Comparison))
    items_count = RPMComparison.comparisons_count(g.db_session)
    return my_render_template(
        'rpm_show_groups.html',
        comparisons=comps,
        items_count=items_count,
        limit=modifiers['limit'],
        offset=modifiers['offset'],
        endpoint='rpmdiff.show_groups',
        arguments={},
    )

@bp.route('/comparisons/<int:id_comp>')
def show_differences(id_comp):
    """Show all rpm differences of one rpm comparison.

    :param int id_comp: id of the comparison
    """
    query = RPMDifference.query(g.db_session)
    query = query.filter(RPMComparison.id == id_comp)
    comparison = dict(iter_query_result(query, RPMDifference))
    return my_render_template(
        'rpm_show_differences.html',
        comparison=comparison
    )

@bp.route('/packages/<int:pkg_id>')
def show_package(pkg_id):
    """Show rpm package.

    :param int pkg_id: id of the package
    """
    query = RPMPackage.query(g.db_session)
    query = query.filter(RPMPackage.id == pkg_id)
    pkgs = dict(iter_query_result(query, RPMPackage))
    return my_render_template(
        'rpm_show_packages.html',
        pkgs=pkgs,
        items_count=1,
        limit=1,
        offset=0,
        endpoint='rpmdiff.show_package',
        arguments={'pkg_id': pkg_id},
    )

@bp.route('/packages/<string:name>')
def show_packages_name(name):
    """Show rpm packages given by name.

    :param string name: package name
    """
    modifiers = get_pagination_modifiers()
    query = RPMPackage.query(g.db_session)
    query = query.filter(RPMPackage.name == name)
    items_count = query.count()
    query = modify_query(query, modifiers)
    pkgs = dict(iter_query_result(query, RPMPackage))
    return my_render_template(
        'rpm_show_packages.html',
        pkgs=pkgs,
        items_count=items_count,
        limit=modifiers['limit'],
        offset=modifiers['offset'],
        endpoint='rpmdiff.show_packages_name',
        arguments={'name': name},
    )

@bp.route('/packages')
def show_packages():
    """Show all rpm packages."""
    modifiers = get_pagination_modifiers()
    query = RPMPackage.query(g.db_session)
    query = modify_query(query, modifiers)
    pkgs = dict(iter_query_result(query, RPMPackage))
    items_count = RPMPackage.count(g.db_session)
    return my_render_template(
        'rpm_show_packages.html',
        pkgs=pkgs,
        items_count=items_count,
        limit=modifiers['limit'],
        offset=modifiers['offset'],
        endpoint='rpmdiff.show_packages',
        arguments={},
    )

@bp.route('/repositories/<int:repo_id>')
def show_repository(repo_id):
    """Show rpm repository.

    :param int repo_id: id of the repository
    """
    query = RPMRepository.query(g.db_session)
    query = query.filter(RPMRepository.id == repo_id)
    repos = dict(iter_query_result(query, RPMRepository))
    return my_render_template(
        'rpm_show_repositories.html',
        repos=repos,
        items_count=1,
        limit=1,
        offset=0,
        endpoint='rpmdiff.show_repository',
        arguments={'repo_id': repo_id},
    )

@bp.route('/repositories')
def show_repositories():
    """Show all rpm repositories."""
    modifiers = get_pagination_modifiers()
    query = RPMRepository.query(g.db_session)
    query = modify_query(query, modifiers)
    repos = dict(iter_query_result(query, RPMRepository))
    items_count = RPMRepository.count(g.db_session)
    return my_render_template(
        'rpm_show_repositories.html',
        repos=repos,
        items_count=items_count,
        limit=modifiers['limit'],
        offset=modifiers['offset'],
        endpoint='rpmdiff.show_repositories',
        arguments={},
    )

@bp.route('/add', methods=['POST'])
def add_entry():
    """Add request for comparison of two rpm packages."""
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
    return redirect(url_for('rpmdiff.index'))

# Resources
def table_by_string(string_table):
    """Convert string to corresponding class.

    :param string string_table: shortened name of the table
    :return: class of the corresponding table
    """
    if string_table == "groups":
        return Comparison
    if string_table == "comparisons":
        return RPMComparison
    if string_table == "differences":
        return RPMDifference
    if string_table == "packages":
        return RPMPackage
    if string_table == "repositories":
        return RPMRepository

class ShowRPMTable(Resource):
    """Show dict of given table."""
    def get(self, string_table):
        """Get dict.

        :param string string_table: shortened name of the table
        :return dict: dict of the resulting query
        """
        table = table_by_string(string_table)
        modifiers = parse_request()
        if table == Comparison:
            query = RPMComparison.comparisons_query(
                g.db_session, modifiers=modifiers
            )
        else:
            query = table.query(g.db_session, modifiers=modifiers)
        return dict(iter_query_result(query, table))

class ShowRPMTableItem(Resource):
    """Show dict of one item of given table."""
    def shown_table(self, table):
        """Determine which table's id is filtered by.

        :param table: class of the table"""
        if table == RPMDifference:
            return RPMComparison
        return table

    def get(self, string_table, id):
        """Get dict.

        :param string string_table: shortened name of the table
        :param int id: id of item from the table
        :return dict: dict of the resulting query
        """
        table = table_by_string(string_table)
        modifiers = parse_request()
        if table == Comparison:
            query = RPMComparison.comparisons_query(
                g.db_session, modifiers=modifiers
            )
        else:
            query = table.query(g.db_session, modifiers=modifiers)
        query = query.filter(self.shown_table(table).id == id)
        return dict(iter_query_result(query, table))

flask_api.add_resource(ShowRPMTable, '/rest/<string:string_table>')
flask_api.add_resource(
    ShowRPMTableItem, '/rest/<string:string_table>/<int:id>'
)
