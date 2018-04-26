#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 11:04:31 2018

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from flask import jsonify
from .flask_app import flask_app

class ApiError(Exception):
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class BadRequest(ApiError):
    status_code = 400

class AuthFailed(ApiError):
    status_code = 401    

@flask_app.errorhandler(ApiError)
def handle_api_error(error):
    """
    :param ApiError error:
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
    