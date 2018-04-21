#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 13:11:04 2018

@author: pavla
"""

from ..rpm_db_models import (RPMComparison, RPMDifference, RPMPackage,
                             RPMRepository, RPMComment)
from .. import constants
from ....flask_frontend import request_parser
from ....flask_frontend.filter_functions import get_first_key

# Functions for making sets of filters
def rpm_comparisons(prefix='comparisons_', relationships=False):
    """Get filters for rpm comparisons.

    :param string prefix: prefix of the name of the filter
    :param bool relationships: True if relationship-related columns should be
        included
    :return dict: dict of filters
    """
    filters = dict(
        **request_parser.equals(
            RPMComparison.id,
            name=prefix + 'id',
            function=(lambda x: int(x))
        ),
        **request_parser.equals(
            RPMComparison.state,
            name=prefix + 'state',
            function=(lambda x: get_first_key(constants.STATE_STRINGS, x))
        ),
    )
    if relationships:
        filters.update(dict(
            **request_parser.equals(
                RPMComparison.id_group,
                name=prefix + 'id_group',
                function=(lambda x: int(x))
            ),
            **request_parser.equals(
                RPMComparison.pkg1_id,
                name=prefix + 'pkg1_id',
                function=(lambda x: int(x))
            ),
            **request_parser.equals(
                RPMComparison.pkg2_id,
                name=prefix + 'pkg2_id',
                function=(lambda x: int(x))
            ),
        ))
    return filters

def rpm_differences(prefix='differences_', relationships=False):
    """Get filters for rpm differences.

    :param string prefix: prefix of the name of the filter
    :param bool relationships: True if relationship-related columns should be
        included
    :return dict: dict of filters
    """
    filters = dict(
        **request_parser.equals(
            RPMDifference.id,
            name=prefix + 'id',
            function=(lambda x: int(x))
        ),
        **request_parser.equals(
            RPMDifference.category,
            name=prefix + 'category',
            function=(lambda x: get_first_key(constants.CATEGORY_STRINGS, x))
        ),
        **request_parser.equals(
            RPMDifference.diff_type,
            name=prefix + 'diff_type',
            function=(lambda x: get_first_key(constants.DIFF_TYPE_STRINGS, x))
        ),
        **request_parser.equals(
            RPMDifference.diff_info,
            name=prefix + 'diff_info'
        ),
        **request_parser.equals(
            RPMDifference.diff,
            name=prefix + 'diff'
        ),
        **request_parser.equals(
            RPMDifference.state,
            name=prefix + 'state',
            function=(lambda x: get_first_key(constants.DIFF_STATE_STRINGS, x))
        ),
    )
    if relationships:
        filters.update(dict(
            **request_parser.equals(
                RPMDifference.id_comp,
                name=prefix + 'comparison_id',
                function=(lambda x: int(x))
            ),
        ))
    return filters

def rpm_packages(table=RPMPackage, prefix='packages_', relationships=False):
    """Get filters for rpm packages.

    :param sqlalchemy.ext.declarative.api.declarativemeta table: database model
    :param string prefix: prefix of the name of the filter
    :param bool relationships: True if relationship-related columns should be
        included
    :return dict: dict of filters
    """
    filters = dict(
        **request_parser.equals(
            table.id,
            name=prefix + 'id',
            function=(lambda x: int(x))
        ),
        **request_parser.equals(table.name, name=prefix + 'name'),
        **request_parser.equals(table.arch, name=prefix + 'arch'),
        **request_parser.equals(table.epoch, name=prefix + 'epoch'),
        **request_parser.equals(table.version, name=prefix + 'version'),
        **request_parser.equals(table.release, name=prefix + 'release'),
    )
    if relationships:
        filters.update(dict(
            **request_parser.equals(
                table.id_repo,
                name=prefix + 'id_repo',
                function=(lambda x: int(x))
            ),
        ))
    return filters

def rpm_repositories(table=RPMRepository, prefix='repositories_'):
    """Get filters for rpm repositories.

    :param sqlalchemy.ext.declarative.api.declarativemeta table: database model
    :param string prefix: prefix of the name of the filter
    :return dict: dict of filters
    """
    filters = dict(
        **request_parser.equals(
            table.id,
            name=prefix + 'id',
            function=(lambda x: int(x))
        ),
        **request_parser.equals(table.path, name=prefix + 'path'),
    )
    return filters

def rpm_comments(table=RPMComment, prefix='comments_', relationships=False):
    """Get filters for rpm comments.

    :param sqlalchemy.ext.declarative.api.declarativemeta table: database model
    :param string prefix: prefix of the name of the filter
    :return dict: dict of filters
    """
    filters = dict(
        **request_parser.equals(
            table.id,
            name=prefix + 'id',
            function=(lambda x: int(x))
        ),
    )
    if relationships:
        filters.update(dict(
            **request_parser.equals(table.id_user, name=prefix + 'id_user'),
            **request_parser.equals(
                table.id_comp,
                name=prefix + 'id_comp',
                function=(lambda x: int(x))
            ),
            **request_parser.equals(
                table.id_diff,
                name=prefix + 'id_diff',
                function=(lambda x: int(x))
            ),
        ))
    return filters
