# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Wed Aug 30 14:55:56 2017

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from flask import render_template, url_for, g
from .flask_app import flask_app
from ..database import session as db_session
from ..database import ComparisonType

def my_render_template(html, **arguments):
    """Call render_template with comparison_types as one of the arguments.

    :param string html: name of the template
    :param **arguments: other arguments to be passed while rendering template
    """
    arguments.setdefault(
        'comparison_types', ComparisonType.get_cache(g.db_session)
    )
    return render_template(html, **arguments)

@flask_app.before_request
def new_database_session():
    """Get new database session for each request."""
    g.db_session = db_session()

@flask_app.teardown_request
def close_database_session(exception):
    """Commit and close database session at the end of request."""
    ses = getattr(g, 'db_session', None)
    if ses is not None:
        try:
            ses.commit()
        except:
            pass
        finally:
            ses.close()

@flask_app.route('/comparison_type_unavailable/<comparison_type>')
def comparison_type_unavailable(comparison_type):
    return my_render_template(
        'comparison_type_unavailable.html', comparison_type=comparison_type
    )

def external_url_handler(error, endpoint, values):
    "Looks up an external URL when `url_for` cannot build a URL."
    for comparison_type in ComparisonType.get_cache(g.db_session).keys():
        if endpoint.startswith(comparison_type):
            return url_for(
                'comparison_type_unavailable', comparison_type=comparison_type
            )
    raise error

flask_app.url_build_error_handlers.append(external_url_handler)
