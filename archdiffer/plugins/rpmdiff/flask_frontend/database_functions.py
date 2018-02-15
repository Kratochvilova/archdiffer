#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 12:24:19 2018

@author: pavla
"""

from flask import g
from sqlalchemy.orm import aliased
from ..rpm_db_models import (RPMComparison, RPMDifference, RPMPackage,
                             RPMRepository)
from ....database import Comparison
from .. import constants

COMPARISON_TYPE = 'rpmdiff'

def joined_query(diffs=False):
    """Query all database tables except rpm_differences.

    :return sqlalchemy.orm.query.Query: resulting query object
    """
    pkg1 = aliased(RPMPackage, name='pkg1')
    pkg2 = aliased(RPMPackage, name='pkg2')
    repo1 = aliased(RPMRepository, name='repo1')
    repo2 = aliased(RPMRepository, name='repo2')
    query = g.db_session.query(
        RPMComparison, Comparison, pkg1, pkg2, repo1, repo2
    ).filter(
        RPMComparison.id_comp==Comparison.id,
        RPMComparison.pkg1_id==pkg1.id,
        RPMComparison.pkg2_id==pkg2.id,
        repo1.id==pkg1.id_repo,
        repo2.id==pkg2.id_repo
    )
    
    if diffs:
        query = query.add_entity(RPMDifference).outerjoin(
            RPMDifference, RPMDifference.id_comp==RPMComparison.id_comp
        )

    return query

def iter_query_result(result, diffs=False):
    def make_comparison(line):
        comp_dict = {
            'time': str(line.Comparison.time),
            'type': COMPARISON_TYPE,
            'pkg1': line.pkg1.exported(),
            'pkg2': line.pkg2.exported(),
            'state': constants.STATE_STRINGS[line.RPMComparison.state],
        }
        comp_dict['pkg1']['repo'] = line.repo1.path
        comp_dict['pkg2']['repo'] = line.repo2.path
        return line.RPMComparison.id_comp, comp_dict

    def get_difference(line, diffs):
        if not diffs or line.RPMDifference is None:
            return
        diff = line.RPMDifference.exported()
        diff['category'] = constants.CATEGORY_STRINGS[diff['category']]
        diff['diff_type'] = constants.DIFF_TYPE_STRINGS[diff['diff_type']]
        return diff

    last_id = None
    comparison = None
    differences = []

    for line in result:
        if last_id is None:
            # Save new id and comparison
            last_id, comparison = make_comparison(line)
        if line.RPMComparison.id_comp != last_id:
            # Add all differences and yield
            if diffs:
                comparison['differences'] = differences
            yield (last_id, comparison)
            # Save new id and comparison
            last_id, comparison = make_comparison(line)
            differences = []
        diff = get_difference(line, diffs)
        if diff is not None:
            differences.append(diff)
    # Add all differences and yield
    if diffs:
        comparison['differences'] = differences
    yield (last_id, comparison)
