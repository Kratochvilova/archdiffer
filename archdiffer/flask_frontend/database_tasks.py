#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 22:32:02 2018

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from operator import attrgetter
from flask import g, current_app
from flask_restful import Resource
from .flask_app import flask_app, flask_api
from ..database import (Comparison, ComparisonType, modify_query,
                        iter_query_result)
from .common_tasks import my_render_template
from . import request_parser
from . import filter_functions

def routes(prefix):
    """Get hierarchical dict of all routes of the current application with
    given prefix.

    :param string prefix: prefix of the routes
    :return dict: routes
    """
    def find_subroutes(string, routes):
        """Find subroutes of rule that is the best prefix of given string.

        :param str string: string to match the prefix
        :param dict routes:
        :return dict: subroutes
        """
        route = ''
        for prefix in routes.keys():
            if string.startswith(prefix):
                route = prefix
        if not route:
            return routes
        else:
            return find_subroutes(string, routes[route]['routes'])

    def add_route(rule, routes):
        """Add new route to dict of routes.

        :param werkzeug.routing.Rule rule:
        :param dict: routes
        """
        routes[rule.rule] = {
            'methods': list(rule.methods),
            'routes': {}
        }
        if 'HEAD' in rule.methods:
            routes[rule.rule]['methods'].remove('HEAD')
        if 'OPTIONS' in rule.methods:
            routes[rule.rule]['methods'].remove('OPTIONS')

    routes = {}
    sorted_rules = sorted(
        current_app.url_map.iter_rules(), key=attrgetter('rule')
    )
    for rule in sorted_rules:
        if rule.rule.startswith(prefix):
            subroutes = find_subroutes(rule.rule, routes)
            add_route(rule, subroutes)
    return routes

class RoutesDict(Resource):
    """Dict of routes."""
    def get(self):
        return routes('/rest')

class TableList(Resource):
    """List of items of given table."""
    table = None
    filters = None
    default_modifiers = {
        'limit': 100,
        'offset': 0,
    }

    def modifiers(self, additional=None):
        """Get modifiers from request arguments.

        :param dict additional: additional modifiers
        :return dict: modifiers
        """
        modifiers = request_parser.parse_request(
            filters=self.filters, defaults=self.default_modifiers
        )
        if additional is not None:
            modifiers = request_parser.update_modifiers(modifiers, additional)
        return modifiers

    def apply_modifiers(self, query, modifiers):
        """Apply modifiers on the query.

        :param sqlalchemy.orm.query.Query query: query
        :param dict modifiers: modifiers
        :return (list, int): (resulting list,
                count of items before apllying limit and offset)
        """
        first = request_parser.get_request_arguments(
            'limit', 'offset', 'order_by', args_dict=modifiers, invert=True
        )
        second = request_parser.get_request_arguments(
            'limit', 'offset', 'order_by', args_dict=modifiers
        )
        query = modify_query(query, first)
        items_count = query.count()
        query = modify_query(query.from_self(), second)
        items = list(iter_query_result(query, self.table))
        return (items, items_count)

    def get(self, id=None):
        """Get list.

        :param int id: id to optionaly filter by
        :return list: list of the items form the resulting query
        """
        query = self.table.query(g.db_session)
        additional_modifiers = None
        if id is not None:
            additional_modifiers = {'filter': [self.table.id == id]}
        modifiers = self.modifiers(additional=additional_modifiers)
        items, _ = self.apply_modifiers(query, modifiers)
        return items

class ComparisonsList(TableList):
    """List of comparisons."""
    table = Comparison
    filters = dict(
        **filter_functions.comparisons(prefix=''),
        **filter_functions.comparison_types()
    )

class ComparisonTypesList(TableList):
    """List of comparison_types."""
    table = ComparisonType
    filters = filter_functions.comparison_types(prefix='')

class ComparisonsView(ComparisonsList):
    """View of comparisons."""
    default_modifiers = {
        'limit': 10, 'offset': 0, 'order_by': [Comparison.id.desc()]
    }

    def dispatch_request(self, id=None):
        """Render template."""
        query = self.table.query(g.db_session)
        additional_modifiers = None
        if id is not None:
            additional_modifiers = {'filter': [self.table.id == id]}
        modifiers = self.modifiers(additional=additional_modifiers)
        comps, items_count = self.apply_modifiers(query, modifiers)

        return my_render_template(
            'show_comparisons.html',
            comparisons=comps,
            items_count=items_count,
            limit=self.modifiers()['limit'],
            offset=self.modifiers()['offset'],
        )

class ComparisonTypesView(ComparisonTypesList):
    """View of comparison types."""
    default_modifiers = {'limit': 10, 'offset': 0}

    def dispatch_request(self):
        """Render template."""
        return my_render_template(
            'show_comparison_types.html',
            items_count=g.db_session.query(ComparisonType).count(),
            limit=self.modifiers()['limit'],
            offset=self.modifiers()['offset'],
        )

flask_api.add_resource(RoutesDict, '/rest')
flask_api.add_resource(
    ComparisonsList, '/rest/comparisons', '/rest/comparisons/<int:id>'
)
flask_api.add_resource(
    ComparisonTypesList,
    '/rest/comparison_types',
    '/rest/comparison_types/<int:id>'
)
flask_app.add_url_rule('/', view_func=ComparisonsView.as_view('index'))
flask_app.add_url_rule(
    '/comparison_types',
    view_func=ComparisonTypesView.as_view('show_comparison_types')
)
