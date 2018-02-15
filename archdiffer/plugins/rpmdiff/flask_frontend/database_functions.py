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

def joined_query(table=RPMComparison):
    """Query database tables jointly.

    :param table: table setting which tables to query
    :type table: one of (RPMDifference, RPMComparison, RPMPackage,
                         RPMRepository)
    :return sqlalchemy.orm.query.Query: resulting query object
    """
    tables = []
    conditions = []

    pkg1 = aliased(RPMPackage, name='pkg1')
    pkg2 = aliased(RPMPackage, name='pkg2')
    repo1 = aliased(RPMRepository, name='repo1')
    repo2 = aliased(RPMRepository, name='repo2')
    
    if table == RPMRepository:
        tables = [repo1]
    if table == RPMPackage:
        tables = [pkg1, repo1]
        conditions = [pkg1.id_repo==repo1.id]
    if table == RPMComparison or table == RPMDifference:
        tables = [Comparison, RPMComparison, pkg1, pkg2, repo1, repo2]
        conditions = [
            RPMComparison.id_comp==Comparison.id,
            RPMComparison.pkg1_id==pkg1.id,
            RPMComparison.pkg2_id==pkg2.id,
            pkg1.id_repo==repo1.id,
            pkg2.id_repo==repo2.id,
        ]

    query = g.db_session.query(*tables).filter(*conditions)

    if table == RPMDifference:
        query = query.add_entity(RPMDifference).outerjoin(
            RPMDifference, RPMDifference.id_comp==RPMComparison.id_comp
        )

    return query

def iter_query_result(result, table=RPMComparison):
    """Process result of the joined query.

    :param table: table setting which tables were queried
    :type table: one of (RPMDifference, RPMComparison, RPMPackage,
                         RPMRepository)
    :return: iterator of resulting dict
    :rtype: Iterator[dict]
    """
    def get_id(line):
        if table == RPMComparison or table == RPMDifference:
            return line.RPMComparison.id_comp
        elif table == RPMPackage:
            return line.pkg1.id
        else:
            return line.id

    def parse_line(line):
        if table == RPMComparison or table == RPMDifference:
            result_dict = {
                'time': str(line.Comparison.time),
                'type': COMPARISON_TYPE,
                'pkg1': line.pkg1.exported(),
                'pkg2': line.pkg2.exported(),
                'state': constants.STATE_STRINGS[line.RPMComparison.state],
            }
            result_dict['pkg1']['repo'] = line.repo1.exported()
            result_dict['pkg2']['repo'] = line.repo2.exported()
            result_dict['pkg1']['filename'] = line.pkg1.rpm_filename()
            result_dict['pkg2']['filename'] = line.pkg2.rpm_filename()
        elif table == RPMPackage:
            result_dict = {'pkg1': line.pkg1.exported()}
            result_dict['pkg1']['repo'] = line.repo1.exported()
            result_dict['pkg1']['filename'] = line.pkg1.rpm_filename()
        else:
            result_dict = {'repo1': line.path}

        return result_dict

    def get_difference(line):
        if table != RPMDifference or line.RPMDifference is None:
            return
        diff = line.RPMDifference.exported()
        diff['category'] = constants.CATEGORY_STRINGS[diff['category']]
        diff['diff_type'] = constants.DIFF_TYPE_STRINGS[diff['diff_type']]
        return diff

    last_id = None
    result_dict = None
    differences = []

    for line in result:
        if last_id is None:
            # Save new id and comparison
            last_id = get_id(line)
            result_dict = parse_line(line)
        if get_id(line) != last_id:
            # Add all differences and yield
            if table == RPMDifference:
                result_dict['differences'] = differences
            yield (last_id, result_dict)
            # Save new id and comparison
            last_id = get_id(line)
            result_dict = parse_line(line)
            differences = []
        diff = get_difference(line)
        if diff is not None:
            differences.append(diff)
    # Add all differences and yield
    if table == RPMDifference:
        result_dict['differences'] = differences
    yield (last_id, result_dict)
