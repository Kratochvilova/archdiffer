#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 22:32:02 2018

@author: pavla
"""

from flask import g
from flask_restful import Resource
from .flask_app import flask_app, flask_api
from ..database import (Comparison, ComparisonType, modify_query,
                        iter_query_result)
from .common_tasks import my_render_template
from . import request_parser
from . import filter_functions

class TableDict(Resource):
    """Dict of given table."""
    table = None
    filters = None
    default_modifiers = None

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
        :return (dict, int): (resulting dict,
                count of items before apllying limit and offset)
        """
        first = request_parser.get_request_arguments(
            'limit', 'offset', args_dict=modifiers, invert=True
        )
        second = request_parser.get_request_arguments(
            'limit', 'offset', args_dict=modifiers
        )
        query = modify_query(query, first)
        items_count = query.count()
        query = modify_query(query, second)
        items = dict(iter_query_result(query, self.table))
        return (items, items_count)

    def get(self, id=None):
        """Get dict.

        :param int id: id to optionaly filter by
        :return dict: dict of the resulting query
        """
        query = self.table.query(g.db_session)
        additional_modifiers = None
        if id is not None:
            additional_modifiers = {'filter': [self.table.id == id]}
        modifiers = self.modifiers(additional=additional_modifiers)
        items, _ = self.apply_modifiers(query, modifiers)
        return items

class ComparisonsDict(TableDict):
    """Dict of comparisons."""
    table = Comparison
    filters = dict(
        **filter_functions.comparisons(prefix=''),
        **filter_functions.comparison_types()
    )

class ComparisonTypesDict(TableDict):
    """Dict of comparison_types."""
    table = ComparisonType
    filters = filter_functions.comparison_types(prefix='')

class ComparisonsView(ComparisonsDict):
    """View of comparisons."""
    default_modifiers = {'limit': 5, 'offset': 0}

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

class ComparisonTypesView(ComparisonTypesDict):
    """View of comparison types."""
    default_modifiers = {'limit': 5, 'offset': 0}

    def dispatch_request(self):
        """Render template."""
        return my_render_template(
            'show_comparison_types.html',
            items_count=ComparisonType.count(g.db_session),
            limit=self.modifiers()['limit'],
            offset=self.modifiers()['offset'],
        )

flask_api.add_resource(
    ComparisonsDict, '/rest/comparisons', '/rest/comparisons/<int:id>'
)
flask_api.add_resource(
    ComparisonTypesDict,
    '/rest/comparison_types',
    '/rest/comparison_types/<int:id>'
)
flask_app.add_url_rule('/', view_func=ComparisonsView.as_view('index'))
flask_app.add_url_rule(
    '/comparison_types',
    view_func=ComparisonTypesView.as_view('show_comparison_types')
)
