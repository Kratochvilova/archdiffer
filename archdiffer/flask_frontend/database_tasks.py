#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 22:32:02 2018

@author: pavla
"""

from flask import request, g
from flask_restful import Resource
from werkzeug.exceptions import BadRequest
from .flask_app import flask_app, flask_api
from ..database import (Comparison, ComparisonType, joined_query,
                        iter_query_result)
from .common_tasks import my_render_template

# Transformation functions for parsing requests
def _dict_transform(string):
    return dict([item.split(':', 1) for item in string.split(';')])

def _list_transform(string):
    return string.split(',')

_TRANSFORMATIONS = {
    'filter_by' : _dict_transform,
    'filter' : _list_transform,
    'order_by' : _list_transform,
    'limit' : lambda x: int(x),
    'offset' : lambda x: int(x),
}

def parse_request():
    """Parse arguments in request according to the _TRANSFORMATIONS.
    Requests containing other keys are considered invalid.

    :return dict: dict of parsed arguments
    """
    args_dict = {}
    for key, value in request.args.items():
        try:
            args_dict[key] = _TRANSFORMATIONS[key](value)
        except:
            raise BadRequest()
    return args_dict

def modify_query(query, modifiers):
    """Modify query according to the modifiers.

    :param query sqlalchemy.orm.query.Query: query to be modified
    :param modifiers dict: dict of modifiers and their values
    :return query sqlalchemy.orm.query.Query: modified query
    """
    if modifiers is None:
        return query
    if 'filter_by' in modifiers:
        query = query.filter_by(**modifiers['filter_by'])
    if 'filter' in modifiers:
        query = query.filter(*modifiers['filter'])
    if 'order_by' in modifiers:
        query = query.order_by(*modifiers['order_by'])
    if 'limit' in modifiers:
        query = query.limit(modifiers['limit'])
    if 'offset' in modifiers:
        query = query.offset(modifiers['offset'])
    return query

def modify_query_by_request(query):
    """Modify query according to the request arguments.

    :param query sqlalchemy.orm.query.Query: query to be modified
    :return query sqlalchemy.orm.query.Query: modified query
    """
    args_dict = parse_request()
    return modify_query(query, args_dict)

@flask_app.route('/')
def index():
    """Show all comparisons."""
    comps = dict(iter_query_result(joined_query(g.db_session)))
    return my_render_template('show_comparisons.html', comparisons=comps)

@flask_app.route('/comparison_types')
def show_comparison_types():
    """Show all comparison types."""
    return my_render_template('show_comparison_types.html')

# Resources
def table_by_string(string_table):
    """Convert string to corresponding class.

    :param string_table string: name of the table
    :return: class of the corresponding table
    """
    if string_table == "comparisons":
        return Comparison
    if string_table == "comparison_types":
        return ComparisonType

class ShowTable(Resource):
    """Show dict of given table."""
    def get(self, string_table):
        """Get dict.

        :param string_table string: name of the table
        :return dict: dict of the resulting query
        """
        table = table_by_string(string_table)
        query = joined_query(g.db_session, table)
        return dict(iter_query_result(modify_query_by_request(query), table))

class ShowTableItem(ShowTable):
    """Show dict of one item of given table."""
    def get(self, string_table, id):
        """Get dict.

        :param string_table string: name of the table
        :param id int: id of item from the table
        :return dict: dict of the resulting query
        """
        table = table_by_string(string_table)
        query = joined_query(g.db_session, table).filter(table.id == id)
        return dict(iter_query_result(modify_query_by_request(query), table))

flask_api.add_resource(ShowTable, '/rest/<string:string_table>')
flask_api.add_resource(ShowTableItem, '/rest/<string:string_table>/<int:id>')
