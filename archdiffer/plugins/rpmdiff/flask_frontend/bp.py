# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Sat Sep 16 22:54:57 2017

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

import json
from flask import (Blueprint, abort, request, flash, redirect, url_for, g,
                   make_response)
from flask import session as flask_session
from flask_restful import Api, Resource
from celery import Celery
from ..rpm_db_models import (RPMComparison, RPMDifference, RPMPackage,
                             RPMRepository, RPMComment, pkg1, pkg2, repo1,
                             repo2, iter_query_result)
from .. import constants
from ....database import Comparison, User, modify_query
from ....flask_frontend.common_tasks import (my_render_template,
                                             rest_api_auth_required)
from ....flask_frontend.database_tasks import TableList, routes
from ....flask_frontend import filter_functions as app_filter_functions
from ....flask_frontend import request_parser
from ....flask_frontend.exceptions import BadRequest
from ....config import config
from . import filter_functions

celery_app = Celery(broker=config['common']['MESSAGE_BROKER'])

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

def add_filter(modifiers, new_filter):
    """Add filter to the modifiers.

    :param dict modifiers: modifiers
    :param sqlalchemy.sql.expression.BinaryExpression new_filter: filter
    :return dict modifiers: new modifiers
    """
    if modifiers is None:
        modifiers = {}
    if 'filter' not in modifiers:
        modifiers['filter'] = []
    modifiers['filter'].append(new_filter)
    return modifiers

class RoutesDict(Resource):
    """Dict of routes."""
    def get(self):
        return routes('/rpmdiff/rest')

class RPMTableList(TableList):
    """List of items of given table."""
    def get(self, id=None):
        """Get list.
        (Overriden because of different iter_query_result function.)

        :param int id: id to optionaly filter by
        :return list: list of the resulting query
        """
        query = self.table.query(g.db_session)
        additional_modifiers = None
        if id is not None:
            additional_modifiers = {'filter': [self.table.id == id]}
        modifiers = self.modifiers(additional=additional_modifiers)
        query = modify_query(query, modifiers)
        return list(iter_query_result(query, self.table))

class RPMGroupsList(RPMTableList):
    """List of comparison groups."""
    table = Comparison
    filters = dict(
        **app_filter_functions.comparisons(prefix=''),
        **filter_functions.rpm_comparisons(prefix='comparisons_'),
        **filter_functions.rpm_packages(table=pkg1, prefix='pkg1_'),
        **filter_functions.rpm_packages(table=pkg2, prefix='pkg2_'),
        **filter_functions.rpm_repositories(table=repo1, prefix='repo1_'),
        **filter_functions.rpm_repositories(table=repo2, prefix='repo2_'),
    )

    def get(self, id=None):
        """Get list.
        (Overriden because of different iter_query_result function.)

        :param int id: id to optionaly filter by
        :return list: list of the resulting query
        """
        query_ids = RPMComparison.query_group_ids(g.db_session)
        additional_modifiers = None
        if id is not None:
            additional_modifiers = {'filter': [self.table.id == id]}
        modifiers = self.modifiers(additional=additional_modifiers)
        query_ids = modify_query(query_ids, modifiers)
        query = RPMComparison.query_groups(g.db_session, query_ids.subquery())
        return list(iter_query_result(query, self.table))

class RPMComparisonsList(RPMTableList):
    """List of rpm comparisons."""
    table = RPMComparison
    filters = dict(
        **filter_functions.rpm_comparisons(prefix=''),
        **app_filter_functions.comparisons(prefix='group_'),
        **filter_functions.rpm_packages(table=pkg1, prefix='pkg1_'),
        **filter_functions.rpm_packages(table=pkg2, prefix='pkg2_'),
        **filter_functions.rpm_repositories(table=repo1, prefix='repo1_'),
        **filter_functions.rpm_repositories(table=repo2, prefix='repo2_'),
    )

    @rest_api_auth_required
    def post(self):
        """Add request for comparison of two rpm packages."""
        try:
            data = json.loads(request.data.decode('utf8'))
        except:
            raise BadRequest(
                "Incorrect data format: please provide dict with 'pkg1' and 'pkg2' dicts."
            )
        pkg1 = {'arch': '', 'epoch': '', 'release': '', 'version': ''}
        pkg2 = {'arch': '', 'epoch': '', 'release': '', 'version': ''}
        try:
            pkg1.update(data['pkg1'])
            pkg2.update(data['pkg2'])
        except KeyError:
            raise BadRequest('Incorrect data format: missing packages.')
        if 'name' not in pkg1 or 'name' not in pkg2:
            raise BadRequest('Incorrect data format: missing package names.')
        if 'repository' not in pkg1 or 'repository' not in pkg2:
            raise BadRequest('Incorrect data format: missing repositories.')

        comp = Comparison.add(g.db_session, constants.COMPARISON_TYPE)

        celery_app.send_task('rpmdiff.compare', args=(comp.id, pkg1, pkg2))

        resp = make_response("", 201)
        resp.headers["Location"] = url_for(
            'rpmdiff.rpmcomparisonslist', id=comp.id
        )
        return resp

class RPMDifferencesList(RPMTableList):
    """List of rpm differences."""
    table = RPMDifference
    filters = dict(
        **RPMComparisonsList.filters.copy(),
        **filter_functions.rpm_differences(),
    )

    def get(self, id=None):
        """Get list.

        :param int id: RPMComparison id
        :return list: list of the resulting query
        """
        query = self.table.query(g.db_session)
        additional_modifiers = None
        if id is not None:
            additional_modifiers = {'filter': [RPMComparison.id == id]}
        modifiers = self.modifiers(additional=additional_modifiers)
        query = modify_query(query, modifiers)
        return list(iter_query_result(query, self.table))

    @rest_api_auth_required
    def put(self, id=None):
        """Waive/unwaive a difference."""
        if id is None:
            raise BadRequest(
                "The method is not allowed for the requested URL."
            )
        try:
            data = json.loads(request.data.decode('utf8'))
        except:
            raise BadRequest(
                "No data: please provide string 'waive' or 'unwaive'."
            )
        diff = g.db_session.query(RPMDifference).filter_by(id=id).first()
        if data == 'waive':
            diff.waive(g.db_session)
        if data == 'unwaive':
            diff.unwaive(g.db_session)
        resp = make_response("", 204)
        return resp

class RPMPackagesList(RPMTableList):
    """List of rpm packages."""
    table = RPMPackage
    filters = dict(
        **filter_functions.rpm_packages(prefix=''),
        **filter_functions.rpm_repositories(),
    )

class RPMRepositoriesList(RPMTableList):
    """List of rpm repositories."""
    table = RPMRepository
    filters = dict(**filter_functions.rpm_repositories(prefix=''))

class RPMCommentsList(RPMTableList):
    """List of rpm comments."""
    table = RPMComment
    filters = dict(
        **filter_functions.rpm_comments(prefix=''),
        **filter_functions.rpm_comparisons(),
        **filter_functions.rpm_differences(),
    )

    def get(self, id=None, username=None, id_comp=None, id_diff=None):
        """Get list.

        :param int id: id to optionally filter by
        :return list: list of the resulting query
        """
        query = self.table.query(g.db_session)
        additional_modifiers = None
        if id is not None:
            additional_modifiers = add_filter(
                additional_modifiers, RPMComment.id == id
            )
        if username is not None:
            additional_modifiers = add_filter(
                additional_modifiers, User.name == username
            )
        if id_comp is not None:
            additional_modifiers = add_filter(
                additional_modifiers, RPMComparison.id == id_comp
            )
        if id_diff is not None:
            additional_modifiers = add_filter(
                additional_modifiers, RPMDifference.id == id_diff
            )
        modifiers = self.modifiers(additional=additional_modifiers)
        query = modify_query(query, modifiers)
        return list(iter_query_result(query, self.table))

    @rest_api_auth_required
    def post(self):
        """Add new comment."""
        try:
            data = json.loads(request.data.decode('utf8'))
        except:
            raise BadRequest(
                "No data: please provide dict with 'text' and either "
                "'id_comp' or 'id_diff'."
            )
        if 'text' not in data:
            if 'id_comp' not in data and 'id_diff' not in data:
                raise BadRequest("Incorrect data format: please provide dict "
                    "with 'text' and either 'id_comp' or 'id_diff'.")
            else:
                raise BadRequest("Incorrect data format: missing "
                    "'text' of the comment.")
        if 'id_comp' not in data and 'id_diff' not in data:
            raise BadRequest(
                'Incorrect data format: missing id of either '
                'comparison or difference (id_comp or id_diff).'
            )
        if 'id_comp' in data and 'id_diff' in data:
            diff = g.db_session.query(RPMDifference).filter_by(
                id=data['id_diff']
            ).first()
            if diff.id_comp != data['id_comp']:
                raise BadRequest(
                    'Incorrect data format: the comparison id does not '
                    'match the difference id.'
                )
        id_comp = None
        id_diff = None
        if 'id_comp' in data:
            id_comp = data['id_comp']
        if 'id_diff' in data:
            id_diff = data['id_diff']

        comment = RPMComment.add(
            g.db_session,
            data['text'],
            g.user.openid,
            id_comp=id_comp,
            id_diff=id_diff
        )

        resp = make_response("", 201)
        resp.headers["Location"] = url_for(
            'rpmdiff.rpmcommentslist', id=comment.id
        )
        return resp

flask_api.add_resource(RoutesDict, '/rest')
flask_api.add_resource(RPMGroupsList, '/rest/groups', '/rest/groups/<int:id>')
flask_api.add_resource(
    RPMComparisonsList, '/rest/comparisons', '/rest/comparisons/<int:id>'
)
flask_api.add_resource(
    RPMDifferencesList, '/rest/differences', '/rest/differences/<int:id>'
)
flask_api.add_resource(
    RPMPackagesList, '/rest/packages', '/rest/packages/<int:id>'
)
flask_api.add_resource(
    RPMRepositoriesList, '/rest/repositories', '/rest/repositories/<int:id>'
)
flask_api.add_resource(
    RPMCommentsList,
    '/rest/comments',
    '/rest/comments/<int:id>',
    '/rest/comments/by_user/<string:username>',
    '/rest/comments/by_comp/<int:id_comp>',
    '/rest/comments/by_diff/<int:id_diff>'
)

class RPMIndexView(RPMGroupsList):
    """View of index."""
    default_modifiers = {
        'limit': 10,
        'offset': 0,
        'order_by': [Comparison.id.desc(), RPMComparison.id.desc()]
    }
    template = 'rpm_show_index.html'

    def dispatch_request(self, id=None):
        """Render template."""
        additional_modifiers = None
        if id is not None:
            additional_modifiers = {'filter': [self.table.id == id]}
        modifiers = self.modifiers(additional=additional_modifiers)

        first = request_parser.get_request_arguments(
            'limit', 'offset', args_dict=modifiers, invert=True
        )
        second = request_parser.get_request_arguments(
            'limit', 'offset', args_dict=modifiers
        )

        query_ids = RPMComparison.query_group_ids(g.db_session)
        query_ids = modify_query(query_ids, first).distinct(Comparison.id)
        items_count = query_ids.count()
        query_ids = modify_query(query_ids, second)
        query = RPMComparison.query_groups(g.db_session, query_ids.subquery())
        query = query.from_self().order_by(*modifiers['order_by'])
        comps = list(iter_query_result(query, self.table))

        return my_render_template(
            self.template,
            comparisons=comps,
            items_count=items_count,
            limit=self.modifiers()['limit'],
            offset=self.modifiers()['offset'],
        )

class RPMComparisonsView(RPMIndexView):
    """View of comparisons."""
    template = 'rpm_show_comparisons.html'
    endpoint = 'rpmdiff.show_comparisons'

class RPMGroupsView(RPMIndexView):
    """View of groups."""
    template = 'rpm_show_groups.html'
    endpoint = 'rpmdiff.show_groups'

class RPMDifferencesView(RPMDifferencesList):
    """View of differences."""
    default_modifiers = {'order_by': [RPMDifference.id]}
    template = 'rpm_show_differences.html'
    endpoint = 'rpmdiff.show_differences'

    def dispatch_request(self, id=None):
        """Render template."""
        comparison = self.get(id=id)
        return my_render_template(self.template, comparison=comparison)

class RPMPackagesView(RPMPackagesList):
    """View of packages."""
    default_modifiers = {
        'limit': 10, 'offset': 0, 'order_by': [RPMPackage.id.desc()]
    }
    template = 'rpm_show_packages.html'

    def dispatch_request(self, id=None, name=None):
        """Render template."""
        query = self.table.query(g.db_session)

        additional_modifiers = None
        if id is not None:
            additional_modifiers = add_filter(
                additional_modifiers, self.table.id == id
            )
        if name is not None:
            additional_modifiers = add_filter(
                additional_modifiers, self.table.name == name
            )
        modifiers = self.modifiers(additional=additional_modifiers)

        pkgs, items_count = self.apply_modifiers(query, modifiers)

        return my_render_template(
            self.template,
            pkgs=pkgs,
            items_count=items_count,
            limit=self.modifiers()['limit'],
            offset=self.modifiers()['offset'],
        )

class RPMRepositoriesView(RPMRepositoriesList):
    """View of repositories."""
    default_modifiers = {
        'limit': 10, 'offset': 0, 'order_by': [RPMRepository.id.desc()]
    }
    template = 'rpm_show_repositories.html'

    def dispatch_request(self, id=None):
        """Render template."""
        query = self.table.query(g.db_session)

        additional_modifiers = None
        if id is not None:
            additional_modifiers = {'filter': [self.table.id == id]}
        modifiers = self.modifiers(additional=additional_modifiers)

        repos, items_count = self.apply_modifiers(query, modifiers)

        return my_render_template(
            self.template,
            repos=repos,
            items_count=items_count,
            limit=self.modifiers()['limit'],
            offset=self.modifiers()['offset'],
        )

class RPMCommentsView(RPMCommentsList):
    """View of comments."""
    default_modifiers = {
        'limit': 10, 'offset': 0, 'order_by': [RPMComment.id.desc()]
    }
    template = 'rpm_show_comments.html'

    def dispatch_request(self, id=None, username=None, id_comp=None,
                         id_diff=None):
        """Render template."""
        query = self.table.query(g.db_session)

        additional_modifiers = None
        if id is not None:
            additional_modifiers = add_filter(
                additional_modifiers, RPMComparison.id == id
            )
        if username is not None:
            additional_modifiers = add_filter(
                additional_modifiers, User.name == username
            )
        if id_comp is not None:
            additional_modifiers = add_filter(
                additional_modifiers, RPMComparison.id == id_comp
            )
        if id_diff is not None:
            additional_modifiers = add_filter(
                additional_modifiers, RPMDifference.id == id_diff
            )
        modifiers = self.modifiers(additional=additional_modifiers)

        comments, items_count = self.apply_modifiers(query, modifiers)

        return my_render_template(
            self.template,
            comments=comments,
            items_count=items_count,
            limit=self.modifiers()['limit'],
            offset=self.modifiers()['offset'],
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
    view_func=RPMPackagesView.as_view('show_packages_name')
)
bp.add_url_rule(
    '/repositories', view_func=RPMRepositoriesView.as_view('show_repositories')
)
bp.add_url_rule(
    '/repositories/<int:id>',
    view_func=RPMRepositoriesView.as_view('show_repository')
)
bp.add_url_rule(
    '/comments', view_func=RPMCommentsView.as_view('show_comments')
)
bp.add_url_rule(
    '/comments/<int:id>',
    view_func=RPMCommentsView.as_view('show_comment')
)
bp.add_url_rule(
    '/comments/by_user/<string:username>',
    view_func=RPMCommentsView.as_view('show_comments_user')
)
bp.add_url_rule(
    '/comments/by_comp/<int:id_comp>',
    view_func=RPMCommentsView.as_view('show_comments_comp')
)
bp.add_url_rule(
    '/comments/by_diff/<int:id_diff>',
    view_func=RPMCommentsView.as_view('show_comments_diff')
)

@bp.route('/new')
def show_new_comparison_form():
    """Show form for new comparison."""
    if g.get('user', None) is None:
        return redirect(
            url_for('login', next=url_for('rpmdiff.show_new_comparison_form'))
        )
    return my_render_template('rpm_show_new_comparison_form.html')

@bp.route('/add_comparison', methods=['POST'])
def add_comparison():
    """Add request for comparison of two rpm packages."""
    if g.get('user', None) is None:
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

    comp = Comparison.add(g.db_session, constants.COMPARISON_TYPE)

    celery_app.send_task('rpmdiff.compare', args=(comp.id, pkg1, pkg2))
    flash('New entry was successfully posted')
    return redirect(url_for('rpmdiff.index'))

@bp.route('/waive', methods=['POST'])
def waive():
    """Waive a difference."""
    if g.get('user', None) is None:
        abort(401)
    id_diff = request.form['id_diff']
    diff = g.db_session.query(RPMDifference).filter_by(id=id_diff).first()
    diff.waive(g.db_session)
    return redirect(
        url_for('rpmdiff.show_differences', id=request.form['id_comp'])
    )

@bp.route('/unwaive', methods=['POST'])
def unwaive():
    """Unwaive a difference."""
    if g.get('user', None) is None:
        abort(401)
    id_diff = request.form['id_diff']
    diff = g.db_session.query(RPMDifference).filter_by(id=id_diff).first()
    diff.unwaive(g.db_session)
    print(request.form['id_comp'])
    return redirect(
        url_for('rpmdiff.show_differences', id=request.form['id_comp'])
    )

@bp.route('/add_comment', methods=['POST'])
def add_comment():
    """Add new comment."""
    if g.get('user', None) is None:
        abort(401)
    id_comp = None
    id_diff = None

    if 'id_comp' in request.form:
        id_comp = request.form['id_comp']
    if 'id_diff' in request.form:
        id_diff = request.form['id_diff']
    RPMComment.add(
        g.db_session,
        request.form['text'],
        flask_session['openid'],
        id_comp=id_comp,
        id_diff=id_diff
    )
    if 'id_diff' in request.form:
        return redirect(
            url_for(
                'rpmdiff.show_comments_diff', id_diff=request.form['id_diff']
            )
        )
    if 'id_comp' in request.form:
        return redirect(
            url_for(
                'rpmdiff.show_comments_comp', id_comp=request.form['id_comp']
            )
        )
    return redirect(
        url_for('rpmdiff.show_comments_user', id_user=flask_session['openid'])
    )
