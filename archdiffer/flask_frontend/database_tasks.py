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
from ..database import Comparison, ComparisonType
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

def modify_query_by_request(query):
    """Modify query according to the request arguments.

    :param query sqlalchemy.orm.query.Query: query to be modified
    :return query sqlalchemy.orm.query.Query: modified query
    """
    args_dict = parse_request()
    if 'filter_by' in args_dict:
        query = query.filter_by(**args_dict['filter_by'])
    if 'filter' in args_dict:
        query = query.filter(*args_dict['filter'])
    if 'order_by' in args_dict:
        query = query.order_by(*args_dict['order_by'])
    if 'limit' in args_dict:
        query = query.limit(args_dict['limit'])
    return query

def joined_query(table=Comparison):
    """Query database tables jointly.

    :param table: table setting which tables to query
    :type table: one of (Comparison, ComparisonType)
    :return sqlalchemy.orm.query.Query: resulting query object
    """
    if table == Comparison:
        return g.db_session.query(Comparison, ComparisonType).filter(
            Comparison.comparison_type_id == ComparisonType.id
        )
    return g.db_session.query(ComparisonType)

def iter_query_result(result, table=Comparison):
    """Process result of the joined query.

    :param table: table setting which tables were queried
    :type table: one of (Comparison, ComparisonType)
    :return: iterator of resulting dict
    :rtype: Iterator[dict]
    """
    def get_id(line):
        if table == Comparison:
            return line.Comparison.id
        return line.id

    def parse_line(line):
        result_dict = {}
        if table == Comparison:
            result_dict['time'] = str(line.Comparison.time)
            result_dict['type'] = {
                'id': line.ComparisonType.id,
                'name': line.ComparisonType.name,
            }
        else:
            result_dict = {'name': line.name}

        return result_dict

    for line in result:
        result_id = get_id(line)
        result_dict = parse_line(line)
        yield (result_id, result_dict)

def query_database_table(table):
    """Query database table according to the request arguments.

    :param table: table to query
    :return list: list of query results
    """
    query = g.db_session.query(table)
    modify_query_by_request(query)

    return query.all()

@flask_app.route('/')
def index():
    comps = dict(iter_query_result(joined_query()))
    return my_render_template('show_comparisons.html', comparisons=comps)

@flask_app.route('/comparison_types')
def show_comparison_types():
    return my_render_template('show_comparison_types.html')

# Resources
class ShowTable(Resource):
    def table_by_string(self, string_table):
        if string_table == "comparisons":
            return Comparison
        if string_table == "comparison_types":
            return ComparisonType

    def get(self, string_table):
        table = self.table_by_string(string_table)
        return dict(iter_query_result(modify_query_by_request(
            joined_query(table)), table
        ))

class ShowTableItem(ShowTable):
    def get(self, string_table, id):
        table = self.table_by_string(string_table)
        query = joined_query(table).filter(table.id == id)
        return dict(iter_query_result(modify_query_by_request(query), table))

flask_api.add_resource(ShowTable, '/rest/<string:string_table>')
flask_api.add_resource(ShowTableItem, '/rest/<string:string_table>/<int:id>')
