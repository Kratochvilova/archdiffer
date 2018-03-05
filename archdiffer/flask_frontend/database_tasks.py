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
from .. import constants
from .common_tasks import my_render_template
from . import request_parser

def get_pagination_modifiers():
    args_dict = request_parser.parse_request(defaults={'limit':5, 'offset':0})
    return request_parser.get_request_arguments('limit', 'offset', args_dict=args_dict)

class TableDict(Resource):
    """Show dict of given table."""
    def table(self):
        """Get table.

        :raises NotImplementedError: this method must be overridden
        """
        raise NotImplementedError

    def modifiers(self):
        """Get modifiers from request arguments.

        :return dict: modifiers
        """
        return request_parser.parse_request()

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
    """Show dict of one item of given table."""    
    def get(self, id):
        """Get dict.

        :param int id: id of item from the table
        :return dict: dict of the resulting query
        """
        query = self.make_query().filter(self.table().id == id)
        return dict(iter_query_result(query, self.table()))

class ComparisonsDict(TableDict):
    """Show dict of comparisons."""
    filters = dict(
        **request_parser.equals(
            Comparison.id,
            function=(lambda x: int(x))
        ),
        **request_parser.equals(
            Comparison.state,
            name='state',
            function=(lambda x: constants.STATE_STRINGS.get(x))
        ),
        **request_parser.equals(
            ComparisonType.id,
            name='comparison_type_id',
            function=(lambda x: int(x))
        ),
        **request_parser.equals(
            ComparisonType.name, name='comparison_type_name'
        ),
        **request_parser.time(Comparison.time),
        **request_parser.before(Comparison.time),
        **request_parser.after(Comparison.time),
    )

    def table(self):
        """Get Comparison table.

        :return sqlalchemy.ext.declarative.api.declarativemeta: Comparison
        """
        return Comparison

    def modifiers(self):
        """Get modifiers from request arguments.

        :return dict: modifiers
        """
        return request_parser.parse_request(filters=self.filters)

class ComparisonsDictItem(ComparisonsDict, TableDictItem):
    """Show dict of one item of comparisons."""

class ComparisonTypesDict(TableDict):
    """Show dict of comparison_types."""
    filters = dict(
        **request_parser.equals(ComparisonType.id),
        **request_parser.equals(ComparisonType.name, name='name'),
    )

    def table(self):
        """Get ComparisonType table.

        :return sqlalchemy.ext.declarative.api.declarativemeta: ComparisonType
        """
        return ComparisonType

    def modifiers(self):
        """Get modifiers from request arguments.

        :return dict: modifiers
        """
        return request_parser.parse_request(filters=self.filters)

class ComparisonTypesDictItem(ComparisonTypesDict, TableDictItem):
    """Show dict of one item of comparison_types."""

class Index(ComparisonsDict):
    """Show comparisons."""
    def modifiers(self, limit=5, offset=0):
        """Get modifiers from request arguments.

        :param int limit: default value for limit
        :param int offset: default value for offset
        :return dict: modifiers
        """
        return request_parser.parse_request(
            filters=self.filters, defaults={'limit': limit, 'offset': offset}
        )

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

class IndexTypes(ComparisonTypesDict):
    """Show comparison types."""
    def modifiers(self, limit=5, offset=0):
        """Get modifiers from request arguments.

        :param int limit: default value for limit
        :param int offset: default value for offset
        :return dict: modifiers
        """
        return request_parser.parse_request(
            filters=self.filters, defaults={'limit': limit, 'offset': offset}
        )

    def dispatch_request(self):
        """Render template."""
        return my_render_template('show_comparison_types.html')

flask_api.add_resource(ComparisonsDict, '/rest/comparisons')
flask_api.add_resource(ComparisonsDictItem, '/rest/comparisons/<int:id>')
flask_api.add_resource(ComparisonTypesDict, '/rest/comparison_types')
flask_api.add_resource(
    ComparisonTypesDictItem, '/rest/comparison_types/<int:id>'
)
flask_app.add_url_rule('/', view_func=Index.as_view('index'))
flask_app.add_url_rule(
    '/comparison_types', view_func=IndexTypes.as_view('show_comparison_types')
)
