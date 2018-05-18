# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Fri May 18 13:41:29 2018

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from ....tests.tests_rest_routes import DATETIMES, IDS, LIMITS, OFFSETS
from .... import constants as app_constants
from .. import constants

GROUP_STATES = list(app_constants.STATE_STRINGS.values())
STATES = list(constants.STATE_STRINGS.values())
CATEGORIES = list(constants.CATEGORY_STRINGS.values())
DIFF_TYPES = list(constants.DIFF_TYPE_STRINGS.values())
DIFF_STATES = list(constants.DIFF_STATE_STRINGS.values())

ROUTES = {
    'comparisons': 'rpmdiff/rest/comparisons',
    'groups': 'rpmdiff/rest/groups',
    'differences': 'rpmdiff/rest/differences',
    'packages': 'rpmdiff/rest/packages',
    'repositories': 'rpmdiff/rest/repositories',
    'comments': 'rpmdiff/rest/comments',    
}

PARAM_CHOICES = {
    'comparisons': {
        'id': IDS,
        'state': STATES,
        'group_id': IDS,
        'group_state': GROUP_STATES,
        'group_before': DATETIMES,
        'group_after': DATETIMES,
        'pkg1_id': IDS,
        'pkg1_name': [''],
        'pkg1_arch': [''],
        'pkg1_epoch': [''],
        'pkg1_version': [''],
        'pkg1_release': [''],
        'pkg2_id': IDS,
        'pkg2_name': [''],
        'pkg2_arch': [''],
        'pkg2_epoch': [''],
        'pkg2_version': [''],
        'pkg2_release': [''],
        'repo1_id': IDS,
        'repo1_path': [''],
        'repo2_id': IDS,
        'repo2_path': [''],
        'limit': LIMITS,
        'offset': OFFSETS,
    },
    'groups': {
        'id': IDS,
        'state': GROUP_STATES,
        'before': DATETIMES,
        'after': DATETIMES,
        'comparisons_id': IDS,
        'comparisons_state': STATES,
        'pkg1_id': IDS,
        'pkg1_name': [''],
        'pkg1_arch': [''],
        'pkg1_epoch': [''],
        'pkg1_version': [''],
        'pkg1_release': [''],
        'pkg2_id': IDS,
        'pkg2_name': [''],
        'pkg2_arch': [''],
        'pkg2_epoch': [''],
        'pkg2_version': [''],
        'pkg2_release': [''],
        'repo1_id': IDS,
        'repo1_path': [''],
        'repo2_id': IDS,
        'repo2_path': [''],
        'limit': LIMITS,
        'offset': OFFSETS,
    },
    'differences': {
        'id': IDS,
        'state': STATES,
        'group_id': IDS,
        'group_state': GROUP_STATES,
        'group_before': DATETIMES,
        'group_after': DATETIMES,
        'pkg1_id': IDS,
        'pkg1_name': [''],
        'pkg1_arch': [''],
        'pkg1_epoch': [''],
        'pkg1_version': [''],
        'pkg1_release': [''],
        'pkg2_id': IDS,
        'pkg2_name': [''],
        'pkg2_arch': [''],
        'pkg2_epoch': [''],
        'pkg2_version': [''],
        'pkg2_release': [''],
        'repo1_id': IDS,
        'repo1_path': [''],
        'repo2_id': IDS,
        'repo2_path': [''],
        'difference_id': IDS,
        'difference_category': CATEGORIES,
        'difference_diff': [''],
        'difference_diff_type': DIFF_TYPES,
        'difference_diff_info': [''],
        'difference_state': DIFF_STATES,
        'difference_waived': ['True', 'False'],
        'limit': LIMITS,
        'offset': OFFSETS,
    },
    'packages': {
        'id': IDS,
        'name': [''],
        'arch': [''],
        'epoch': [''],
        'version': [''],
        'release': [''],
        'repository_id': IDS,
        'repository_path': [''],
        'limit': LIMITS,
        'offset': OFFSETS,
    },
    'repositories': {
        'id': IDS,
        'path': [''],
        'limit': LIMITS,
        'offset': OFFSETS,
    },
    'comments': {
        'id': IDS,
        'comparison_id': IDS,
        'comparison_state': STATES,
        'difference_id': IDS,
        'difference_category': CATEGORIES,
        'difference_diff': [''],
        'difference_diff_type': DIFF_TYPES,
        'difference_diff_info': [''],
        'difference_state': DIFF_STATES,
        'difference_waived': ['True', 'False'],        
        'limit': LIMITS,
        'offset': OFFSETS,
    },
}
