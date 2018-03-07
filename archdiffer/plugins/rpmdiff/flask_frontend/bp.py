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
from ....database import Comparison
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
    def get(self, id=None):
        """Get dict.
        (Overriden because of different iter_query_result function.)

        :param int id: id to optionaly filter by
        :return dict: dict of the resulting query
        """
        additional_modifiers = None
        if id is not None:
            additional_modifiers = {'filter': [self.table.id == id]}
        query = self.make_query(additional_modifiers=additional_modifiers)
        return dict(iter_query_result(query, self.table))

class RPMTableDictOuter(RPMTableDict):
    """Dict of given table, implementing outer modifiers."""
    def modifiers(self, additional=None):
        """Get modifiers from request arguments, only limit and offset.

        :return dict: modifiers
        """
        modifiers = request_parser.parse_request(
            filters=self.filters, defaults=self.default_modifiers
        )
        if additional is not None:
            modifiers = request_parser.update_modifiers(modifiers, additional)
        return request_parser.get_request_arguments(
            'limit', 'offset', args_dict=modifiers
        )

    def outer_modifiers(self, additional=None):
        """Get modifiers from request arguments, exclude limit and offset.

        :return dict: modifiers
        """
        modifiers = request_parser.parse_request(
            filters=self.filters, defaults=self.default_modifiers
        )
        if additional is not None:
            modifiers = request_parser.update_modifiers(modifiers, additional)
        return request_parser.get_request_arguments(
            'limit', 'offset', args_dict=modifiers, invert=True
        )

    def make_query(self, additional_modifiers=None):
        """Call query method on the table with modifiers and outer_modifiers
        as arguments.

        :return sqlalchemy.orm.query.Query result: query
        """
        return self.table.query(
            g.db_session,
            modifiers=self.modifiers(),
            outer_modifiers=self.outer_modifiers(
                additional=additional_modifiers
            )
        )

class RPMGroupsDict(RPMTableDictOuter):
    """Dict of comparison groups."""
    table = Comparison
    filters = dict(
        **app_filter_functions.comparisons(prefix=''),
        **filter_functions.rpm_comparisons(prefix='comparisons_'),
        **filter_functions.rpm_packages(table=pkg1, prefix='pkg1_'),
        **filter_functions.rpm_packages(table=pkg2, prefix='pkg2_'),
        **filter_functions.rpm_repositories(table=repo1, prefix='repo1_'),
        **filter_functions.rpm_repositories(table=repo2, prefix='repo2_'),
    )

    def make_query(self, additional_modifiers=None):
        """Call query method on the table with modifiers and outer_modifiers
        as arguments.

        :return sqlalchemy.orm.query.Query result: query
        """
        return RPMComparison.comparisons_query(
            g.db_session,
            modifiers=self.modifiers(),
            outer_modifiers=self.outer_modifiers(
                additional=additional_modifiers
            )
        )

class RPMComparisonsDict(RPMTableDict):
    """Dict of rpm comparisons."""
    table = RPMComparison
    filters = dict(
        **filter_functions.rpm_comparisons(prefix=''),
        **app_filter_functions.comparisons(prefix='groups_'),
        **filter_functions.rpm_packages(table=pkg1, prefix='pkg1_'),
        **filter_functions.rpm_packages(table=pkg2, prefix='pkg2_'),
        **filter_functions.rpm_repositories(table=repo1, prefix='repo1_'),
        **filter_functions.rpm_repositories(table=repo2, prefix='repo2_'),
    )

class RPMDifferencesDict(RPMTableDictOuter):
    """Dict of rpm differences."""
    table = RPMDifference
    filters = dict(
        **RPMComparisonsDict.filters.copy(),
        **filter_functions.rpm_differences(),
    )

    def get(self, id=None):
        """Get dict.

        :param int id: RPMComparison id
        :return dict: dict of the resulting query
        """
        additional_modifiers = None
        if id is not None:
            additional_modifiers = {'filter': [RPMComparison.id == id]}
        query = self.make_query(additional_modifiers=additional_modifiers)
        return dict(iter_query_result(query, self.table))

class RPMPackagesDict(RPMTableDict):
    """Dict of rpm packages."""
    table = RPMPackage
    filters = dict(
        **filter_functions.rpm_packages(prefix=''),
        **filter_functions.rpm_repositories(),
    )

class RPMRepositoriesDict(RPMTableDict):
    """Dict of rpm repositories."""
    table = RPMRepository
    filters = dict(**filter_functions.rpm_repositories(prefix=''))

flask_api.add_resource(RPMGroupsDict, '/rest/groups', '/rest/groups/<int:id>')
flask_api.add_resource(
    RPMComparisonsDict, '/rest/comparisons', '/rest/comparisons/<int:id>'
)
flask_api.add_resource(
    RPMDifferencesDict, '/rest/differences', '/rest/differences/<int:id>'
)
flask_api.add_resource(
    RPMPackagesDict, '/rest/packages', '/rest/packages/<int:id>'
)
flask_api.add_resource(
    RPMRepositoriesDict, '/rest/repositories', '/rest/repositories/<int:id>'
)

class RPMIndexView(RPMGroupsDict):
    """View of index."""
    default_modifiers = {'limit': 5, 'offset': 0}
    template = 'rpm_show_index.html'
    endpoint = 'rpmdiff.index'

    def dispatch_request(self, id=None):
        """Render template."""
        comps = self.get(id=id)
        items_count = len(comps)

        return my_render_template(
            self.template,
            comparisons=comps,
            items_count=items_count,
            limit=self.modifiers()['limit'],
            offset=self.modifiers()['offset'],
            endpoint=self.endpoint,
            arguments={'id': id},
        )

class RPMComparisonsView(RPMIndexView):
    """View of comparisons."""
    template = 'rpm_show_comparisons.html'
    endpoint = 'rpmdiff.show_comparisons'

class RPMGroupsView(RPMIndexView):
    """View of groups."""
    template = 'rpm_show_groups.html'
    endpoint = 'rpmdiff.show_groups'

class RPMDifferencesView(RPMDifferencesDict):
    """View of differences."""
    template = 'rpm_show_differences.html'
    endpoint = 'rpmdiff.show_differences'

    def dispatch_request(self, id=None):
        """Render template."""
        comparison = self.get(id=id)
        return my_render_template(self.template, comparison=comparison)

class RPMPackagesView(RPMPackagesDict):
    """View of packages."""
    default_modifiers = {'limit': 5, 'offset': 0}
    template = 'rpm_show_packages.html'
    endpoint = 'rpmdiff.show_package'

    def dispatch_request(self, id=None):
        """Render template."""
        pkgs = self.get(id=id)
        items_count = len(pkgs)
        return my_render_template(
            self.template,
            pkgs=pkgs,
            items_count=items_count,
            limit=self.modifiers()['limit'],
            offset=self.modifiers()['offset'],
            endpoint=self.endpoint,
            arguments={'id': id},
        )

class RPMPackagesNameView(RPMPackagesDict):
    """View of packages."""
    default_modifiers = {'limit': 5, 'offset': 0}
    template = 'rpm_show_packages.html'
    endpoint = 'rpmdiff.show_packages_name'

    def dispatch_request(self, name):
        """Render template."""
        additional_modifiers = None
        if name is not None:
            additional_modifiers = {'filter': [RPMPackage.name == name]}
        query = self.make_query(additional_modifiers=additional_modifiers)
        pkgs = dict(iter_query_result(query, self.table))
        items_count = len(pkgs)

        return my_render_template(
            self.template,
            pkgs=pkgs,
            items_count=items_count,
            limit=self.modifiers()['limit'],
            offset=self.modifiers()['offset'],
            endpoint=self.endpoint,
            arguments={'name': name},
        )

class RPMRepositoriesView(RPMRepositoriesDict):
    """View of packages."""
    default_modifiers = {'limit': 5, 'offset': 0}
    template = 'rpm_show_repositories.html'
    endpoint = 'rpmdiff.show_repositories'

    def dispatch_request(self, id=None):
        """Render template."""
        repos = self.get(id=id)
        items_count = len(repos)
        return my_render_template(
            self.template,
            repos=repos,
            items_count=items_count,
            limit=self.modifiers()['limit'],
            offset=self.modifiers()['offset'],
            endpoint=self.endpoint,
            arguments={'id': id},
        )

bp.add_url_rule('/', view_func=RPMIndexView.as_view('index'))
bp.add_url_rule(
    '/comparisons', view_func=RPMComparisonsView.as_view('show_comparisons')
)
bp.add_url_rule('/groups', view_func=RPMGroupsView.as_view('show_groups'))
bp.add_url_rule(
    '/groups/<int:id>', view_func=RPMGroupsView.as_view('show_group')
)
bp.add_url_rule(
    '/comparisons/<int:id>',
    view_func=RPMDifferencesView.as_view('show_differences')
)
bp.add_url_rule(
    '/packages', view_func=RPMPackagesView.as_view('show_packages')
)
bp.add_url_rule(
    '/packages/<int:id>', view_func=RPMPackagesView.as_view('show_package')
)
bp.add_url_rule(
    '/packages/<string:name>',
    view_func=RPMPackagesNameView.as_view('show_packages_name')
)
bp.add_url_rule(
    '/repositories', view_func=RPMRepositoriesView.as_view('show_repositories')
)
bp.add_url_rule(
    '/repositories/<int:id>',
    view_func=RPMRepositoriesView.as_view('show_repository')
)

@bp.route('/new')
def show_new_comparison_form():
    """Show form for new comparison."""
    return my_render_template('rpm_show_new_comparison_form.html')

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
