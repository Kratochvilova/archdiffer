# -*- coding: utf-8 -*-
"""
Created on Sun Aug 27 15:32:45 2017

@author: pavla
"""

from . import zipdiff_flask, zipdiff_worker
from ...repository import register_comparator, register_blueprint

register_comparator('zipdiff', zipdiff_worker.compare)
register_blueprint('zipdiff', zipdiff_flask.bp_zipdiff)
