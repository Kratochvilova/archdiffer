#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 22:32:02 2018

@author: pavla
"""


from flask import request, g
from flask.views import View
from flask_restful import Resource
from flask_restful import fields, marshal_with
from .flask_app import flask_app, flask_api
from ..database import Comparison, ComparisonType
from .common_tasks import my_render_template

# For marshalling sqlalchemy objects
comparison_fields = {
    'id': fields.Integer,
    'time': fields.String,
    'comparison_type_id': fields.Integer
}

comparison_type_fields = {
    'id': fields.Integer,
    'name': fields.String
}

# Transformation functions for parsing requests
def _dict_transform(string):
    return dict([item.split(':', 1) for item in string.split(';')])

def _list_transform(string):
    return string.split(',')

_TRANSFORMATIONS = {
    'filter_by' : _dict_transform,
    'order_by' : _list_transform,
    'limit' : lambda x: int(x),
}

def parse_request():
    args_dict = {}
    for key, value in request.args.items():
        args_dict[key] = _TRANSFORMATIONS[key](value)
    return args_dict

def query_database_table(table_name):
    result = g.db_session.query(table_name)
    args_dict = parse_request()
    if 'filter_by' in args_dict:
        result = result.filter_by(**args_dict['filter_by'])
    if 'order_by' in args_dict:
        result = result.order_by(*args_dict['order_by'])
    if 'limit' in args_dict:
        result = result.all()[:args_dict['limit']]
    else:
        result = result.all()

    return result

# Comparisons
class ShowComparisons(Resource):
    @marshal_with(comparison_fields)
    def get(self):
        return query_database_table(Comparison)

class ComparisonsView(View):
    def dispatch_request(self):
        return my_render_template('show_comparisons.html', comparisons=query_database_table(Comparison))

flask_api.add_resource(ShowComparisons, '/rest/comparisons/')
flask_app.add_url_rule('/', view_func=ComparisonsView.as_view('index'))

# Comparison types
class ShowComparisonTypes(Resource):
    @marshal_with(comparison_fields)
    def get(self):
        return query_database_table(ComparisonType)

class ComparisonTypesView(View):
    def dispatch_request(self):
        return my_render_template('show_comparison_types.html')

flask_api.add_resource(ShowComparisonTypes, '/rest/comparison_types/')
flask_app.add_url_rule('/comparison_types', view_func=ComparisonTypesView.as_view('show_comparison_types'))

