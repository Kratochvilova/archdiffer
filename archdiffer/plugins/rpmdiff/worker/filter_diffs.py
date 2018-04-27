#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Fri Mar  9 09:01:53 2018

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from .... import database
from ....backend.celery_app import celery_app
from ..rpm_db_models import RPMComparison, RPMDifference
from .. import constants

RULES = [RPMDifference.category == 1, RPMDifference.diff_type == 0]
RULES = []

@celery_app.task(name='rpmdiff.filter_diffs')
def filter_diffs(id_comp):
    """Compare two packages and write results to the database.

    :param dict pkg1: first package dict with keys:
        name, arch, epoch, version, release, repository
    :param dict pkg2: second package dict
    """
    session = database.session()

    diffs = session.query(RPMDifference).filter_by(id_comp=id_comp)
    for rule in RULES:
        filtered_diffs = diffs.filter(rule)
        for diff in filtered_diffs.all():
            diff.state = constants.DIFF_STATE_IGNORED
            session.add(diff)

    comp = session.query(RPMComparison).filter_by(id=id_comp).one()
    comp.update_state(session, constants.STATE_DONE)

    try:
        session.commit()
    except:
        session.rollback()
        print("Couldn't add filter changes to the database.")
