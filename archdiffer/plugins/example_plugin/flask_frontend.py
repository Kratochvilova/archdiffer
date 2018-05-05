# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Wed May  2 15:58:46 2018

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from flask import Blueprint, request, render_template, redirect, url_for
from celery import Celery
from ...flask_frontend.flask_app import flask_app
from ...config import config

# Blueprint named example_plugin. If you want templates or static files,
# you can provide template_folder or static_folder parameter.
blueprint = Blueprint('example_plugin', __name__, template_folder='templates')

# Celery app for sending tasks via celery.
celery_app = Celery(broker=config['common']['MESSAGE_BROKER'])

# Some index page.
@blueprint.route('/', methods=['GET'])
def index():
    """Some index page."""
    return render_template('example_plugin_index.html')

# View that sends celery task named example_plugin.example_task with data from
# request form as argument.
@blueprint.route('/send_task', methods=['POST'])
def send_task():
    """Send an example task."""
    data = request.form['data']
    celery_app.send_task('example_plugin.example_task', args=(data))
    return redirect(url_for('example_plugin.index'))

# Register the blueprint and set unique prefix.
flask_app.register_blueprint(blueprint, url_prefix='/'+'example_plugin')
