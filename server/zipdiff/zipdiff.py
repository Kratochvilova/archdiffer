# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 12:09:08 2017

@author: pavla
"""

from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

bp_zipdiff = Blueprint('zipdiff', __name__, template_folder='templates')

@bp_zipdiff.route('/')
def show():
    try:
        return render_template('page.html')
    except TemplateNotFound:
        abort(404)
