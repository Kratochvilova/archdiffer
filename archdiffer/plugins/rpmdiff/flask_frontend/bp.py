# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 22:54:57 2017

@author: pavla
"""

from flask import Blueprint, abort, request, flash, redirect, url_for, g
from flask import session as flask_session
from flask_restful import Api
from celery import Celery
from ..rpm_db_models import (RPMComparison, RPMDifference, RPMPackage,
                             RPMRepository, pkg1, pkg2, repo1, repo2,
                             iter_query_result)
from .. import constants
from ....database import Comparison, ComparisonType, modify_query
from ....flask_frontend.common_tasks import my_render_template
from ....flask_frontend.database_tasks import TableDict
from ....flask_frontend import filter_functions as app_filter_functions
from ....flask_frontend import request_parser
from . import filter_functions

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

class RPMTableDict(TableDict):
    """Dict of given table."""
    def get(self, id):
        """Get dict.

        :param int id: id to optionaly filter by
        :return dict: dict of the resulting query
        """
        query = self.make_query()
        if id is not None:
            query = query.filter(self.table().id == id)
        return dict(iter_query_result(query, self.table()))

class RPMTableDictOuter(RPMTableDict):
    """Dict of given table, implementing outer modifiers."""
    def modifiers(self):
        """Get modifiers from request arguments, only limit and offset.

        :return dict: modifiers
        """
        modifiers = request_parser.parse_request(filters=self.filters)
        return request_parser.get_request_arguments(
            'limit', 'offset', args_dict=modifiers
        )

    def outer_modifiers(self):
        """Get modifiers from request arguments, exclude limit and offset.

        :return dict: modifiers
        """
        modifiers = request_parser.parse_request(filters=self.filters)
        try:
            modifiers.pop('limit')
        except KeyError:
            pass
        try:
            modifiers.pop('offset')
        except KeyError:
            pass
        return modifiers

    def make_query(self):
        """Call query method on the table with modifiers and outer_modifiers
        as arguments.

        :return sqlalchemy.orm.query.Query result: query
        """
        return self.table().query(
            g.db_session,
            modifiers=self.modifiers(),
            outer_modifiers=self.outer_modifiers()
        )

class GroupsDict(RPMTableDictOuter):
    """Dict of comparison groups."""
    filters = dict(
        **app_filter_functions.comparisons(prefix=''),
        **filter_functions.rpm_comparisons(prefix='comparisons_'),
        **filter_functions.rpm_packages(table=pkg1, prefix='pkg1_'),
        **filter_functions.rpm_packages(table=pkg2, prefix='pkg2_'),
        **filter_functions.rpm_repositories(table=repo1, prefix='repo1_'),
        **filter_functions.rpm_repositories(table=repo2, prefix='repo2_'),
    )

    def table(self):
        """Get Comparison table.

        :return sqlalchemy.ext.declarative.api.declarativemeta: Comparison
        """
        return Comparison

    def make_query(self):
        """Call query method on the table with modifiers and outer_modifiers
        as arguments.

        :return sqlalchemy.orm.query.Query result: query
        """
        return RPMComparison.comparisons_query(
            g.db_session,
            modifiers=self.modifiers(),
            outer_modifiers=self.outer_modifiers()
        )

class RPMComparisonsDict(RPMTableDict):
    """Dict of rpm comparisons."""
    filters = dict(
        **filter_functions.rpm_comparisons(prefix=''),
        **app_filter_functions.comparisons(prefix='groups_'),
        **filter_functions.rpm_packages(table=pkg1, prefix='pkg1_'),
        **filter_functions.rpm_packages(table=pkg2, prefix='pkg2_'),
        **filter_functions.rpm_repositories(table=repo1, prefix='repo1_'),
        **filter_functions.rpm_repositories(table=repo2, prefix='repo2_'),
    )

    def table(self):
        """Get RPMComparison table.

        :return sqlalchemy.ext.declarative.api.declarativemeta: RPMComparison
        """
        return RPMComparison

class RPMDifferencesDict(RPMTableDictOuter):
    """Dict of rpm differences."""
    filters = dict(
        **RPMComparisonsDict.filters.copy(),
        **filter_functions.rpm_differences(),
    )

    def table(self):
        """Get RPMDifference table.

        :return sqlalchemy.ext.declarative.api.declarativemeta: RPMDifference
        """
        return RPMDifference

    def get(self, id):
        """Get dict.

        :param int id: RPMComparison id
        :return dict: dict of the resulting query
        """
        query = self.make_query()
        if id is not None:
            query = query.filter(RPMComparison.id == id)
        return dict(iter_query_result(query, self.table()))

class RPMPackagesDict(RPMTableDict):
    """Dict of rpm packages."""
    filters = dict(
        **filter_functions.rpm_packages(prefix=''),
        **filter_functions.rpm_repositories(),
    )

    def table(self):
        """Get RPMPackage table.

        :return sqlalchemy.ext.declarative.api.declarativemeta: RPMPackage
        """
        return RPMPackage

class RPMRepositoriesDict(RPMTableDict):
    """Dict of rpm repositories."""
    filters = dict(**filter_functions.rpm_repositories(prefix=''))

    def table(self):
        """Get RPMRepository table.

        :return sqlalchemy.ext.declarative.api.declarativemeta: RPMRepository
        """
        return RPMRepository

flask_api.add_resource(GroupsDict, '/rest/groups', '/rest/groups/<int:id>')
flask_api.add_resource(RPMComparisonsDict, '/rest/comparisons', '/rest/comparisons/<int:id>')
flask_api.add_resource(RPMDifferencesDict, '/rest/differences', '/rest/differences/<int:id>')
flask_api.add_resource(RPMPackagesDict, '/rest/packages', '/rest/packages/<int:id>')
flask_api.add_resource(RPMRepositoriesDict, '/rest/repositories', '/rest/repositories/<int:id>')

class ComparisonsView(GroupsDict):
    """View of comparisons."""
    default_modifiers = {'limit': 5, 'offset': 0}

    def dispatch_request(self):
        """Render template."""
        query = self.make_query()
        items_count = query.count()
        comps = dict(iter_query_result(query, Comparison))

        return my_render_template(
            'rpm_show_index.html',
            comparisons=comps,
            items_count=items_count,
            limit=self.modifiers()['limit'],
            offset=self.modifiers()['offset'],
            endpoint='rpmdiff.index',
            arguments={},
        )

bp.add_url_rule('/', view_func=ComparisonsView.as_view('index'))

@bp.route('/comparisons')
def show_comparisons():
    """Show all comparisons."""
    modifiers = request_parser.get_pagination_modifiers(
        defaults={'limit': 5, 'offset': 0}
    )
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
    modifiers = request_parser.get_pagination_modifiers(
        defaults={'limit': 5, 'offset': 0}
    )
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
    modifiers = request_parser.get_pagination_modifiers(
        defaults={'limit': 5, 'offset': 0}
    )
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
    modifiers = request_parser.get_pagination_modifiers(
        defaults={'limit': 5, 'offset': 0}
    )
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
    modifiers = request_parser.get_pagination_modifiers(
        defaults={'limit': 5, 'offset': 0}
    )
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
    modifiers = request_parser.get_pagination_modifiers(
        defaults={'limit': 5, 'offset': 0}
    )
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
    pkg1_dict = {
        'name': request.form['name1'],
        'arch': request.form['arch1'],
        'epoch': request.form['epoch1'],
        'version': request.form['version1'],
        'release': request.form['release1'],
        'repository': request.form['repo1'],
    }
    pkg2_dict = {
        'name': request.form['name2'],
        'arch': request.form['arch2'],
        'epoch': request.form['epoch2'],
        'version': request.form['version2'],
        'release': request.form['release2'],
        'repository': request.form['repo2'],
    }
    celery_app.send_task(
        'rpmdiff.compare', args=(pkg1_dict, pkg2_dict)
    )
    flash('New entry was successfully posted')
    return redirect(url_for('rpmdiff.index'))
