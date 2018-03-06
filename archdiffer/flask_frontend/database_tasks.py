#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 22:32:02 2018

@author: pavla
"""

from flask import g
from flask_restful import Resource
from .flask_app import flask_app, flask_api
from ..database import Comparison, ComparisonType, iter_query_result
from .common_tasks import my_render_template
from . import request_parser
from . import filter_functions

class TableDict(Resource):
    """Dict of given table."""
    filters = None
    default_modifiers = None

    def table(self):
        """Get table.

        :raises NotImplementedError: this method must be overridden
        """
        raise NotImplementedError

    def modifiers(self):
        """Get modifiers from request arguments.

        :return dict: modifiers
        """
        return request_parser.parse_request(
            filters=self.filters, defaults=self.default_modifiers
        )

    def make_query(self):
        """Call query method on the table with modifiers as argument.

        :return sqlalchemy.orm.query.Query result: query
        """
        return self.table().query(g.db_session, modifiers=self.modifiers())

    def get(self):
        """Get dict.

        :return dict: dict of the resulting query
        """
        return dict(iter_query_result(self.make_query(), self.table()))

class TableDictItem(TableDict):
    """Dict of one item of given table."""
    def get(self, id):
        """Get dict.

        :param int id: id of item from the table
        :return dict: dict of the resulting query
        """
        query = self.make_query().filter(self.table().id == id)
        return dict(iter_query_result(query, self.table()))

class ComparisonsDict(TableDict):
    """Dict of comparisons."""
    filters = dict(
        **filter_functions.comparisons(prefix=''),
        **filter_functions.comparison_types()
    )

    def table(self):
        """Get Comparison table.

        :return sqlalchemy.ext.declarative.api.declarativemeta: Comparison
        """
        return Comparison

class ComparisonsDictItem(ComparisonsDict, TableDictItem):
    """Dict of one item of comparisons."""

class ComparisonTypesDict(TableDict):
    """Dict of comparison_types."""
    filters = filter_functions.comparison_types(prefix='')

    def table(self):
        """Get ComparisonType table.

        :return sqlalchemy.ext.declarative.api.declarativemeta: ComparisonType
        """
        return ComparisonType

class ComparisonsView(ComparisonsDict):
    """View of comparisons."""
    default_modifiers = {'limit': 5, 'offset': 0}

    def dispatch_request(self):
        """Render template."""
        query = self.make_query()
        items_count = query.count()
        comps = dict(iter_query_result(query, Comparison))

        return my_render_template(
            'show_comparisons.html',
            comparisons=comps,
            items_count=items_count,
            limit=self.modifiers()['limit'],
            offset=self.modifiers()['offset'],
            endpoint='index',
            arguments={},
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
            endpoint='index',
            arguments={},
        )
        return my_render_template('show_comparison_types.html')

flask_api.add_resource(ComparisonsDict, '/rest/comparisons')
flask_api.add_resource(ComparisonsDictItem, '/rest/comparisons/<int:id>')
flask_api.add_resource(ComparisonTypesDict, '/rest/comparison_types')
flask_api.add_resource(
    ComparisonTypesDictItem, '/rest/comparison_types/<int:id>'
)
flask_app.add_url_rule('/', view_func=ComparisonsView.as_view('index'))
flask_app.add_url_rule(
    '/comparison_types',
    view_func=ComparisonTypesView.as_view('show_comparison_types')
)
