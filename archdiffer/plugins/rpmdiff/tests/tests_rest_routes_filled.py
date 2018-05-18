# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Thu May 17 13:20:29 2018

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from datetime import datetime
from ....tests.tests_rest_routes import RESTTestListsFilled
from .... import constants as app_constants
from .... import database
from .. import constants
from .. import rpm_db_models
from .tests_rest_constants import ROUTES, PARAM_CHOICES

class RESTTestRpmdiffComparisonsFilled(RESTTestListsFilled):
    """Tests for getting comparisons from filled database."""
    route = ROUTES['comparisons']
    param_choices = PARAM_CHOICES['comparisons']

    def fill_db(self):
        """Fill database. Called in setUp."""
        db_session = database.session()
        comparison_types = [database.ComparisonType(id=1, name='rpmdiff')]
        comparisons = [
            database.Comparison(
                id=1, state=0, time=datetime(1000, 1, 1), comparison_type_id=1
            ),
            database.Comparison(
                id=2, state=1, time=datetime(2018, 1, 1), comparison_type_id=1
            ),
        ]
        rpm_repositories = [
            rpm_db_models.RPMRepository(id=1, path='repo1'),
            rpm_db_models.RPMRepository(id=2, path='repo2'),
        ]
        rpm_packages = [
            rpm_db_models.RPMPackage(
                id=1,
                name='name1',
                arch='arch1',
                epoch='epoch1',
                version='version1',
                release='release1',
                id_repo=1
            ),
            rpm_db_models.RPMPackage(
                id=2,
                name='name2',
                arch='arch2',
                epoch='epoch2',
                version='version2',
                release='release2',
                id_repo=2
            ),
        ]
        rpm_comparisons = [
            rpm_db_models.RPMComparison(
                id=1, id_group=1, pkg1_id=1, pkg2_id=2, state=0
            ),
            rpm_db_models.RPMComparison(
                id=2, id_group=2, pkg1_id=2, pkg2_id=2, state=0
            ),
            rpm_db_models.RPMComparison(
                id=3, id_group=2, pkg1_id=2, pkg2_id=1, state=1
            ),
        ]
        db_session.add_all(comparison_types)
        db_session.add_all(comparisons)
        db_session.add_all(rpm_repositories)
        db_session.add_all(rpm_packages)
        db_session.add_all(rpm_comparisons)
        db_session.commit()
        db_session.close()

    # Expected result for request without any parameters.
    expected = [
        {
            'id': 1,
            'id_group': 1,
            'state': constants.STATE_STRINGS[0],
            'time': '1000-01-01 00:00:00',
            'type': 'rpmdiff',
            'pkg1': {
                'id': 1,
                'name': 'name1',
                'filename': 'name1-version1-release1.arch1.rpm',
                'arch': 'arch1',
                'epoch': 'epoch1',
                'version': 'version1',
                'release': 'release1',
                'repo': {
                    'id': 1,
                    'path': 'repo1'
                },
            },
            'pkg2': {
                'id': 2,
                'name': 'name2',
                'filename': 'name2-version2-release2.arch2.rpm',
                'arch': 'arch2',
                'epoch': 'epoch2',
                'version': 'version2',
                'release': 'release2',
                'repo': {
                    'id': 2,
                    'path': 'repo2'
                },
            },
        },
        {
            'id': 2,
            'id_group': 2,
            'state': constants.STATE_STRINGS[0],
            'time':'2018-01-01 00:00:00',
            'type': 'rpmdiff',
            'pkg1': {
                'id': 2,
                'name': 'name2',
                'filename': 'name2-version2-release2.arch2.rpm',
                'arch': 'arch2',
                'epoch': 'epoch2',
                'version': 'version2',
                'release': 'release2',
                'repo': {
                    'id': 2,
                    'path': 'repo2'
                },
            },
            'pkg2': {
                'id': 2,
                'name': 'name2',
                'filename': 'name2-version2-release2.arch2.rpm',
                'arch': 'arch2',
                'epoch': 'epoch2',
                'version': 'version2',
                'release': 'release2',
                'repo': {
                    'id': 2,
                    'path': 'repo2'
                },
            },
        },
        {
            'id': 3,
            'id_group': 2,
            'state': constants.STATE_STRINGS[1],
            'time': '2018-01-01 00:00:00',
            'type': 'rpmdiff',
            'pkg1': {
                'id': 2,
                'name': 'name2',
                'filename': 'name2-version2-release2.arch2.rpm',
                'arch': 'arch2',
                'epoch': 'epoch2',
                'version': 'version2',
                'release': 'release2',
                'repo': {
                    'id': 2,
                    'path': 'repo2'
                },
            },
            'pkg2': {
                'id': 1,
                'name': 'name1',
                'filename': 'name1-version1-release1.arch1.rpm',
                'arch': 'arch1',
                'epoch': 'epoch1',
                'version': 'version1',
                'release': 'release1',
                'repo': {
                    'id': 1,
                    'path': 'repo1'
                },
            },
        },
    ]

    # Tuples of query parameters and corresponding expected result.
    tuples_params_results = [
        ({}, expected),
        ({'id': '2'}, [expected[1]]),
        ({'state': constants.STATE_STRINGS[1]}, [expected[2]]),
        ({'group_id': '1'}, [expected[0]]),
        (
            {'group_state': app_constants.STATE_STRINGS[1]},
            [expected[1], expected[2]]
        ),
        ({'group_before': '2000-01-01 00:00:00'}, [expected[0]]),
        ({'group_after': '2000-01-01 00:00:00'}, [expected[1], expected[2]]),
        ({'pkg1_id': '1'}, [expected[0]]),
        ({'pkg1_name': 'name1'}, [expected[0]]),
        ({'pkg1_arch': 'arch1'}, [expected[0]]),
        ({'pkg1_epoch': 'epoch1'}, [expected[0]]),
        ({'pkg1_version': 'version1'}, [expected[0]]),
        ({'pkg1_release': 'release1'}, [expected[0]]),
        ({'pkg2_id': '2'}, [expected[0], expected[1]]),
        ({'pkg2_name': 'name2'}, [expected[0], expected[1]]),
        ({'pkg2_arch': 'arch2'}, [expected[0], expected[1]]),
        ({'pkg2_epoch': 'epoch2'}, [expected[0], expected[1]]),
        ({'pkg2_version': 'version2'}, [expected[0], expected[1]]),
        ({'pkg2_release': 'release2'}, [expected[0], expected[1]]),
        ({'repo1_id': '2'}, [expected[1], expected[2]]),
        ({'repo2_id': '2'}, [expected[0], expected[1]]),
        ({'limit': '2'}, [expected[0], expected[1]]),
        ({'offset': '2'}, [expected[2]]),
        ({'pkg2_arch': 'arch2', 'offset': 1}, [expected[1]]),
    ]

class RESTTestRpmdiffGroupsFilled(RESTTestListsFilled):
    """Tests for getting comparison groups from filled database."""
    route = ROUTES['groups']
    param_choices = PARAM_CHOICES['groups']

    def fill_db(self):
        """Fill database. Called in setUp."""
        db_session = database.session()
        comparison_types = [database.ComparisonType(id=1, name='rpmdiff')]
        comparisons = [
            database.Comparison(
                id=1, state=0, time=datetime(1000, 1, 1), comparison_type_id=1
            ),
            database.Comparison(
                id=2, state=1, time=datetime(2018, 1, 1), comparison_type_id=1
            ),
            database.Comparison(
                id=3, state=1, time=datetime(2000, 1, 1), comparison_type_id=1
            ),
        ]
        rpm_repositories = [
            rpm_db_models.RPMRepository(id=1, path='repo1'),
            rpm_db_models.RPMRepository(id=2, path='repo2'),
        ]
        rpm_packages = [
            rpm_db_models.RPMPackage(
                id=1,
                name='name1',
                arch='arch1',
                epoch='epoch1',
                version='version1',
                release='release1',
                id_repo=1
            ),
            rpm_db_models.RPMPackage(
                id=2,
                name='name2',
                arch='arch2',
                epoch='epoch2',
                version='version2',
                release='release2',
                id_repo=2
            ),
        ]
        rpm_comparisons = [
            rpm_db_models.RPMComparison(
                id=1, id_group=1, pkg1_id=1, pkg2_id=2, state=0
            ),
            rpm_db_models.RPMComparison(
                id=2, id_group=2, pkg1_id=2, pkg2_id=2, state=0
            ),
            rpm_db_models.RPMComparison(
                id=3, id_group=2, pkg1_id=2, pkg2_id=1, state=1
            ),
        ]
        db_session.add_all(comparison_types)
        db_session.add_all(comparisons)
        db_session.add_all(rpm_repositories)
        db_session.add_all(rpm_packages)
        db_session.add_all(rpm_comparisons)
        db_session.commit()
        db_session.close()

    # Expected result for request without any parameters.
    expected = [
        {
            'id': 1,
            'state': app_constants.STATE_STRINGS[0],
            'time': '1000-01-01 00:00:00',
            'type': 'rpmdiff',
            'comparisons': [
                {
                    'id': 1,
                    'id_group': 1,
                    'state': constants.STATE_STRINGS[0],
                    'time': '1000-01-01 00:00:00',
                    'type': 'rpmdiff',
                    'pkg1': {
                        'id': 1,
                        'name': 'name1',
                        'filename': 'name1-version1-release1.arch1.rpm',
                        'arch': 'arch1',
                        'epoch': 'epoch1',
                        'version': 'version1',
                        'release': 'release1',
                        'repo': {
                            'id': 1,
                            'path': 'repo1'
                        },
                    },
                    'pkg2': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                },
            ],
        },
        {
            'id': 2,
            'state': app_constants.STATE_STRINGS[1],
            'time': '2018-01-01 00:00:00',
            'type': 'rpmdiff',
            'comparisons': [
                {
                    'id': 2,
                    'id_group': 2,
                    'state': constants.STATE_STRINGS[0],
                    'time':'2018-01-01 00:00:00',
                    'type': 'rpmdiff',
                    'pkg1': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                    'pkg2': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                },
                {
                    'id': 3,
                    'id_group': 2,
                    'state': constants.STATE_STRINGS[1],
                    'time': '2018-01-01 00:00:00',
                    'type': 'rpmdiff',
                    'pkg1': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                    'pkg2': {
                        'id': 1,
                        'name': 'name1',
                        'filename': 'name1-version1-release1.arch1.rpm',
                        'arch': 'arch1',
                        'epoch': 'epoch1',
                        'version': 'version1',
                        'release': 'release1',
                        'repo': {
                            'id': 1,
                            'path': 'repo1'
                        },
                    },
                },
            ],
        },
        {
            'id': 3,
            'state': app_constants.STATE_STRINGS[1],
            'time': '2000-01-01 00:00:00',
            'type': 'rpmdiff',
            'comparisons': [],
        },
    ]

    # Tuples of query parameters and corresponding expected result.
    tuples_params_results = [
        ({}, expected),
        ({'id': '2'}, [expected[1]]),
        ({'state': app_constants.STATE_STRINGS[1]}, [expected[1], expected[2]]),
        ({'before': '2001-01-01 00:00:00'}, [expected[0], expected[2]]),
        ({'after': '2001-01-01 00:00:00'}, [expected[1]]),
        ({'comparisons_id': 2}, [expected[1]]),
        ({'comparisons_state': constants.STATE_STRINGS[1]}, [expected[1]]),
        ({'pkg1_id': '1'}, [expected[0]]),
        ({'pkg1_name': 'name1'}, [expected[0]]),
        ({'pkg1_arch': 'arch1'}, [expected[0]]),
        ({'pkg1_epoch': 'epoch1'}, [expected[0]]),
        ({'pkg1_version': 'version1'}, [expected[0]]),
        ({'pkg1_release': 'release1'}, [expected[0]]),
        ({'pkg2_id': '2'}, [expected[0], expected[1]]),
        ({'pkg2_name': 'name2'}, [expected[0], expected[1]]),
        ({'pkg2_arch': 'arch2'}, [expected[0], expected[1]]),
        ({'pkg2_epoch': 'epoch2'}, [expected[0], expected[1]]),
        ({'pkg2_version': 'version2'}, [expected[0], expected[1]]),
        ({'pkg2_release': 'release2'}, [expected[0], expected[1]]),
        ({'repo1_id': '2'}, [expected[1]]),
        ({'repo2_id': '2'}, [expected[0], expected[1]]),
        ({'limit': '2'}, [expected[0], expected[1]]),
        ({'offset': '2'}, [expected[2]]),
        (
            {'comparisons_state': constants.STATE_STRINGS[0], 'offset': 1},
            [expected[1]]
        ),
    ]

class RESTTestRpmdiffDifferencesFilled(RESTTestListsFilled):
    """Tests for getting differences from filled database."""
    route = ROUTES['differences']
    param_choices = PARAM_CHOICES['differences']

    def fill_db(self):
        """Fill database. Called in setUp."""
        db_session = database.session()
        comparison_types = [database.ComparisonType(id=1, name='rpmdiff')]
        comparisons = [
            database.Comparison(
                id=1, state=0, time=datetime(1000, 1, 1), comparison_type_id=1
            ),
        ]
        rpm_repositories = [
            rpm_db_models.RPMRepository(id=1, path='repo1'),
            rpm_db_models.RPMRepository(id=2, path='repo2'),
        ]
        rpm_packages = [
            rpm_db_models.RPMPackage(
                id=1,
                name='name1',
                arch='arch1',
                epoch='epoch1',
                version='version1',
                release='release1',
                id_repo=1
            ),
            rpm_db_models.RPMPackage(
                id=2,
                name='name2',
                arch='arch2',
                epoch='epoch2',
                version='version2',
                release='release2',
                id_repo=2
            ),
        ]
        rpm_comparisons = [
            rpm_db_models.RPMComparison(
                id=1, id_group=1, pkg1_id=1, pkg2_id=2, state=0
            ),
            rpm_db_models.RPMComparison(
                id=2, id_group=1, pkg1_id=2, pkg2_id=2, state=0
            ),
            rpm_db_models.RPMComparison(
                id=3, id_group=1, pkg1_id=2, pkg2_id=1, state=1
            ),
        ]
        rpm_differences = [
            rpm_db_models.RPMDifference(
                id=1, id_comp=1, category=0, diff_type=0,
                diff_info='diff_info1', diff='diff1', state=0, waived=False,
            ),
            rpm_db_models.RPMDifference(
                id=2, id_comp=1, category=1, diff_type=0,
                diff_info='diff_info2', diff='diff1', state=1, waived=True,
            ),
            rpm_db_models.RPMDifference(
                id=3, id_comp=2, category=0, diff_type=1,
                diff_info='diff_info3', diff='diff2', state=2, waived=False,
            ),
            rpm_db_models.RPMDifference(
                id=4, id_comp=2, category=1, diff_type=1,
                diff_info='diff_info1', diff='diff3', state=2, waived=False,
            ),
            rpm_db_models.RPMDifference(
                id=5, id_comp=2, category=0, diff_type=0,
                diff_info='diff_info1', diff='diff3', state=0, waived=False,
            ),
        ]
        db_session.add_all(comparison_types)
        db_session.add_all(comparisons)
        db_session.add_all(rpm_repositories)
        db_session.add_all(rpm_packages)
        db_session.add_all(rpm_comparisons)
        db_session.add_all(rpm_differences)
        db_session.commit()
        db_session.close()

    # Expected result for request without any parameters.
    expected = [
        {
            'id': 1,
            'id_group': 1,
            'state': constants.STATE_STRINGS[0],
            'time': '1000-01-01 00:00:00',
            'type': 'rpmdiff',
            'pkg1': {
                'id': 1,
                'name': 'name1',
                'filename': 'name1-version1-release1.arch1.rpm',
                'arch': 'arch1',
                'epoch': 'epoch1',
                'version': 'version1',
                'release': 'release1',
                'repo': {
                    'id': 1,
                    'path': 'repo1'
                },
            },
            'pkg2': {
                'id': 2,
                'name': 'name2',
                'filename': 'name2-version2-release2.arch2.rpm',
                'arch': 'arch2',
                'epoch': 'epoch2',
                'version': 'version2',
                'release': 'release2',
                'repo': {
                    'id': 2,
                    'path': 'repo2'
                },
            },
            'differences': [
                {
                    'id': 1,
                    'category': constants.CATEGORY_STRINGS[0],
                    'diff_type': constants.DIFF_TYPE_STRINGS[0],
                    'diff_info': 'diff_info1',
                    'diff': 'diff1',
                    'state': constants.DIFF_STATE_STRINGS[0],
                    'waived': False,
                },
                {
                    'id': 2,
                    'category': constants.CATEGORY_STRINGS[1],
                    'diff_type': constants.DIFF_TYPE_STRINGS[0],
                    'diff_info': 'diff_info2',
                    'diff': 'diff1',
                    'state': constants.DIFF_STATE_STRINGS[1],
                    'waived': True,
                },
            ],
        },
        {
            'id': 2,
            'id_group': 1,
            'state': constants.STATE_STRINGS[0],
            'time':'1000-01-01 00:00:00',
            'type': 'rpmdiff',
            'pkg1': {
                'id': 2,
                'name': 'name2',
                'filename': 'name2-version2-release2.arch2.rpm',
                'arch': 'arch2',
                'epoch': 'epoch2',
                'version': 'version2',
                'release': 'release2',
                'repo': {
                    'id': 2,
                    'path': 'repo2'
                },
            },
            'pkg2': {
                'id': 2,
                'name': 'name2',
                'filename': 'name2-version2-release2.arch2.rpm',
                'arch': 'arch2',
                'epoch': 'epoch2',
                'version': 'version2',
                'release': 'release2',
                'repo': {
                    'id': 2,
                    'path': 'repo2'
                },
            },
            'differences': [
                {
                    'id': 3,
                    'category': constants.CATEGORY_STRINGS[0],
                    'diff_type': constants.DIFF_TYPE_STRINGS[1],
                    'diff_info': 'diff_info3',
                    'diff': 'diff2',
                    'state': constants.DIFF_STATE_STRINGS[2],
                    'waived': False,
                },
                {
                    'id': 4,
                    'category': constants.CATEGORY_STRINGS[1],
                    'diff_type': constants.DIFF_TYPE_STRINGS[1],
                    'diff_info': 'diff_info1',
                    'diff': 'diff3',
                    'state': constants.DIFF_STATE_STRINGS[2],
                    'waived': False,
                },
                {
                    'id': 5,
                    'category': constants.CATEGORY_STRINGS[0],
                    'diff_type': constants.DIFF_TYPE_STRINGS[0],
                    'diff_info': 'diff_info1',
                    'diff': 'diff3',
                    'state': constants.DIFF_STATE_STRINGS[0],
                    'waived': False,
                },
            ],
        },
        {
            'id': 3,
            'id_group': 1,
            'state': constants.STATE_STRINGS[1],
            'time': '1000-01-01 00:00:00',
            'type': 'rpmdiff',
            'pkg1': {
                'id': 2,
                'name': 'name2',
                'filename': 'name2-version2-release2.arch2.rpm',
                'arch': 'arch2',
                'epoch': 'epoch2',
                'version': 'version2',
                'release': 'release2',
                'repo': {
                    'id': 2,
                    'path': 'repo2'
                },
            },
            'pkg2': {
                'id': 1,
                'name': 'name1',
                'filename': 'name1-version1-release1.arch1.rpm',
                'arch': 'arch1',
                'epoch': 'epoch1',
                'version': 'version1',
                'release': 'release1',
                'repo': {
                    'id': 1,
                    'path': 'repo1'
                },
            },
            'differences': [],
        },
    ]

    # Tuples of query parameters and corresponding expected result.
    tuples_params_results = [
        ({}, expected),
        ({'id': '2'}, [expected[1]]),
        ({'state': constants.STATE_STRINGS[1]}, [expected[2]]),
        ({'group_id': '1'}, expected),
        ({'group_state': app_constants.STATE_STRINGS[0]}, expected),
        ({'group_before': '2000-01-01 00:00:00'}, expected),
        ({'group_after': '2000-01-01 00:00:00'}, []),
        ({'pkg1_id': '1'}, [expected[0]]),
        ({'pkg1_name': 'name1'}, [expected[0]]),
        ({'pkg1_arch': 'arch1'}, [expected[0]]),
        ({'pkg1_epoch': 'epoch1'}, [expected[0]]),
        ({'pkg1_version': 'version1'}, [expected[0]]),
        ({'pkg1_release': 'release1'}, [expected[0]]),
        ({'pkg2_id': '2'}, [expected[0], expected[1]]),
        ({'pkg2_name': 'name2'}, [expected[0], expected[1]]),
        ({'pkg2_arch': 'arch2'}, [expected[0], expected[1]]),
        ({'pkg2_epoch': 'epoch2'}, [expected[0], expected[1]]),
        ({'pkg2_version': 'version2'}, [expected[0], expected[1]]),
        ({'pkg2_release': 'release2'}, [expected[0], expected[1]]),
        ({'repo1_id': '2'}, [expected[1], expected[2]]),
        ({'repo2_id': '2'}, [expected[0], expected[1]]),
        ({'limit': '2'}, [expected[0]]),
        ({'offset': '2'}, [expected[1], expected[2]]),
        (
            {'difference_id': '3'},
            [
                {
                    'id': 2,
                    'id_group': 1,
                    'state': constants.STATE_STRINGS[0],
                    'time':'1000-01-01 00:00:00',
                    'type': 'rpmdiff',
                    'pkg1': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                    'pkg2': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                    'differences': [
                        {
                            'id': 3,
                            'category': constants.CATEGORY_STRINGS[0],
                            'diff_type': constants.DIFF_TYPE_STRINGS[1],
                            'diff_info': 'diff_info3',
                            'diff': 'diff2',
                            'state': constants.DIFF_STATE_STRINGS[2],
                            'waived': False,
                        },
                    ],
                },
            ]
        ),
        (
            {'difference_category': constants.CATEGORY_STRINGS[0]},
            [
                {
                    'id': 1,
                    'id_group': 1,
                    'state': constants.STATE_STRINGS[0],
                    'time': '1000-01-01 00:00:00',
                    'type': 'rpmdiff',
                    'pkg1': {
                        'id': 1,
                        'name': 'name1',
                        'filename': 'name1-version1-release1.arch1.rpm',
                        'arch': 'arch1',
                        'epoch': 'epoch1',
                        'version': 'version1',
                        'release': 'release1',
                        'repo': {
                            'id': 1,
                            'path': 'repo1'
                        },
                    },
                    'pkg2': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                    'differences': [
                        {
                            'id': 1,
                            'category': constants.CATEGORY_STRINGS[0],
                            'diff_type': constants.DIFF_TYPE_STRINGS[0],
                            'diff_info': 'diff_info1',
                            'diff': 'diff1',
                            'state': constants.DIFF_STATE_STRINGS[0],
                            'waived': False,
                        },
                    ],
                },
                {
                    'id': 2,
                    'id_group': 1,
                    'state': constants.STATE_STRINGS[0],
                    'time':'1000-01-01 00:00:00',
                    'type': 'rpmdiff',
                    'pkg1': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                    'pkg2': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                    'differences': [
                        {
                            'id': 3,
                            'category': constants.CATEGORY_STRINGS[0],
                            'diff_type': constants.DIFF_TYPE_STRINGS[1],
                            'diff_info': 'diff_info3',
                            'diff': 'diff2',
                            'state': constants.DIFF_STATE_STRINGS[2],
                            'waived': False,
                        },
                        {
                            'id': 5,
                            'category': constants.CATEGORY_STRINGS[0],
                            'diff_type': constants.DIFF_TYPE_STRINGS[0],
                            'diff_info': 'diff_info1',
                            'diff': 'diff3',
                            'state': constants.DIFF_STATE_STRINGS[0],
                            'waived': False,
                        },
                    ],
                },
            ]
        ),
        (
            {'difference_diff': 'diff3'},
            [
                {
                    'id': 2,
                    'id_group': 1,
                    'state': constants.STATE_STRINGS[0],
                    'time':'1000-01-01 00:00:00',
                    'type': 'rpmdiff',
                    'pkg1': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                    'pkg2': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                    'differences': [
                        {
                            'id': 4,
                            'category': constants.CATEGORY_STRINGS[1],
                            'diff_type': constants.DIFF_TYPE_STRINGS[1],
                            'diff_info': 'diff_info1',
                            'diff': 'diff3',
                            'state': constants.DIFF_STATE_STRINGS[2],
                            'waived': False,
                        },
                        {
                            'id': 5,
                            'category': constants.CATEGORY_STRINGS[0],
                            'diff_type': constants.DIFF_TYPE_STRINGS[0],
                            'diff_info': 'diff_info1',
                            'diff': 'diff3',
                            'state': constants.DIFF_STATE_STRINGS[0],
                            'waived': False,
                        },
                    ],
                },
            ]
        ),
        (
            {'difference_diff_type': constants.DIFF_TYPE_STRINGS[0]},
            [
                {
                    'id': 1,
                    'id_group': 1,
                    'state': constants.STATE_STRINGS[0],
                    'time': '1000-01-01 00:00:00',
                    'type': 'rpmdiff',
                    'pkg1': {
                        'id': 1,
                        'name': 'name1',
                        'filename': 'name1-version1-release1.arch1.rpm',
                        'arch': 'arch1',
                        'epoch': 'epoch1',
                        'version': 'version1',
                        'release': 'release1',
                        'repo': {
                            'id': 1,
                            'path': 'repo1'
                        },
                    },
                    'pkg2': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                    'differences': [
                        {
                            'id': 1,
                            'category': constants.CATEGORY_STRINGS[0],
                            'diff_type': constants.DIFF_TYPE_STRINGS[0],
                            'diff_info': 'diff_info1',
                            'diff': 'diff1',
                            'state': constants.DIFF_STATE_STRINGS[0],
                            'waived': False,
                        },
                        {
                            'id': 2,
                            'category': constants.CATEGORY_STRINGS[1],
                            'diff_type': constants.DIFF_TYPE_STRINGS[0],
                            'diff_info': 'diff_info2',
                            'diff': 'diff1',
                            'state': constants.DIFF_STATE_STRINGS[1],
                            'waived': True,
                        },
                    ],
                },
                {
                    'id': 2,
                    'id_group': 1,
                    'state': constants.STATE_STRINGS[0],
                    'time':'1000-01-01 00:00:00',
                    'type': 'rpmdiff',
                    'pkg1': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                    'pkg2': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                    'differences': [
                        {
                            'id': 5,
                            'category': constants.CATEGORY_STRINGS[0],
                            'diff_type': constants.DIFF_TYPE_STRINGS[0],
                            'diff_info': 'diff_info1',
                            'diff': 'diff3',
                            'state': constants.DIFF_STATE_STRINGS[0],
                            'waived': False,
                        },
                    ],
                },
            ]
        ),
        (
            {'difference_diff_info': 'diff_info2'},
            [
                {
                    'id': 1,
                    'id_group': 1,
                    'state': constants.STATE_STRINGS[0],
                    'time': '1000-01-01 00:00:00',
                    'type': 'rpmdiff',
                    'pkg1': {
                        'id': 1,
                        'name': 'name1',
                        'filename': 'name1-version1-release1.arch1.rpm',
                        'arch': 'arch1',
                        'epoch': 'epoch1',
                        'version': 'version1',
                        'release': 'release1',
                        'repo': {
                            'id': 1,
                            'path': 'repo1'
                        },
                    },
                    'pkg2': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                    'differences': [
                        {
                            'id': 2,
                            'category': constants.CATEGORY_STRINGS[1],
                            'diff_type': constants.DIFF_TYPE_STRINGS[0],
                            'diff_info': 'diff_info2',
                            'diff': 'diff1',
                            'state': constants.DIFF_STATE_STRINGS[1],
                            'waived': True,
                        },
                    ],
                },
            ]
        ),
        (
            {'difference_state': constants.DIFF_STATE_STRINGS[2]},
            [
                {
                    'id': 2,
                    'id_group': 1,
                    'state': constants.STATE_STRINGS[0],
                    'time':'1000-01-01 00:00:00',
                    'type': 'rpmdiff',
                    'pkg1': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                    'pkg2': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                    'differences': [
                        {
                            'id': 3,
                            'category': constants.CATEGORY_STRINGS[0],
                            'diff_type': constants.DIFF_TYPE_STRINGS[1],
                            'diff_info': 'diff_info3',
                            'diff': 'diff2',
                            'state': constants.DIFF_STATE_STRINGS[2],
                            'waived': False,
                        },
                        {
                            'id': 4,
                            'category': constants.CATEGORY_STRINGS[1],
                            'diff_type': constants.DIFF_TYPE_STRINGS[1],
                            'diff_info': 'diff_info1',
                            'diff': 'diff3',
                            'state': constants.DIFF_STATE_STRINGS[2],
                            'waived': False,
                        },
                    ],
                },
            ]
        ),
        (
            {'difference_waived': 'true'},
            [
                {
                    'id': 1,
                    'id_group': 1,
                    'state': constants.STATE_STRINGS[0],
                    'time': '1000-01-01 00:00:00',
                    'type': 'rpmdiff',
                    'pkg1': {
                        'id': 1,
                        'name': 'name1',
                        'filename': 'name1-version1-release1.arch1.rpm',
                        'arch': 'arch1',
                        'epoch': 'epoch1',
                        'version': 'version1',
                        'release': 'release1',
                        'repo': {
                            'id': 1,
                            'path': 'repo1'
                        },
                    },
                    'pkg2': {
                        'id': 2,
                        'name': 'name2',
                        'filename': 'name2-version2-release2.arch2.rpm',
                        'arch': 'arch2',
                        'epoch': 'epoch2',
                        'version': 'version2',
                        'release': 'release2',
                        'repo': {
                            'id': 2,
                            'path': 'repo2'
                        },
                    },
                    'differences': [
                        {
                            'id': 2,
                            'category': constants.CATEGORY_STRINGS[1],
                            'diff_type': constants.DIFF_TYPE_STRINGS[0],
                            'diff_info': 'diff_info2',
                            'diff': 'diff1',
                            'state': constants.DIFF_STATE_STRINGS[1],
                            'waived': True,
                        },
                    ],
                },
            ]
        ),
    ]

class RESTTestRpmdiffPackagesFilled(RESTTestListsFilled):
    """Tests for getting packages from filled database."""
    route = ROUTES['packages']
    param_choices = PARAM_CHOICES['packages']

    def fill_db(self):
        """Fill database. Called in setUp."""
        db_session = database.session()
        rpm_repositories = [
            rpm_db_models.RPMRepository(id=1, path='repo1'),
            rpm_db_models.RPMRepository(id=2, path='repo2'),
        ]
        rpm_packages = [
            rpm_db_models.RPMPackage(
                id=1,
                name='nameA',
                arch='archA',
                epoch='epoch1',
                version='version1',
                release='release1',
                id_repo=2
            ),
            rpm_db_models.RPMPackage(
                id=2,
                name='nameA',
                arch='archB',
                epoch='epoch2',
                version='version2',
                release='release2',
                id_repo=2
            ),
            rpm_db_models.RPMPackage(
                id=3,
                name='nameB',
                arch='archB',
                epoch='epoch3',
                version='version3',
                release='release3',
                id_repo=1
            ),
        ]
        db_session.add_all(rpm_repositories)
        db_session.add_all(rpm_packages)
        db_session.commit()
        db_session.close()

    # Expected result for request without any parameters.
    expected = [
        {
            'id': 1,
            'name': 'nameA',
            'arch': 'archA',
            'epoch': 'epoch1',
            'version': 'version1',
            'release': 'release1',
            'filename': 'nameA-version1-release1.archA.rpm',
            'repo': {
                'id': 2,
                'path': 'repo2',
            },
        },
        {
            'id': 2,
            'name': 'nameA',
            'arch': 'archB',
            'epoch': 'epoch2',
            'version': 'version2',
            'release': 'release2',
            'filename': 'nameA-version2-release2.archB.rpm',
            'repo': {
                'id': 2,
                'path': 'repo2',
            },
        },
        {
            'id': 3,
            'name': 'nameB',
            'arch': 'archB',
            'epoch': 'epoch3',
            'version': 'version3',
            'release': 'release3',
            'filename': 'nameB-version3-release3.archB.rpm',
            'repo': {
                'id': 1,
                'path': 'repo1',
            },
        },
    ]

    # Tuples of query parameters and corresponding expected result.
    tuples_params_results = [
        ({}, expected),
        ({'id': '2'}, [expected[1]]),
        ({'name': 'nameA'}, [expected[0], expected[1]]),
        ({'arch': 'archA'}, [expected[0]]),
        ({'epoch': 'epoch1'}, [expected[0]]),
        ({'version': 'version1'}, [expected[0]]),
        ({'release': 'release1'}, [expected[0]]),
        ({'repository_id': '1'}, [expected[2]]),
        ({'repository_path': 'repo1'}, [expected[2]]),
        ({'limit': '1'}, [expected[0]]),
        ({'offset': '2'}, [expected[2]]),
        ({'name': 'nameA', 'arch': 'archB'}, [expected[1]]),
    ]

class RESTTestRpmdiffRepositoriesFilled(RESTTestListsFilled):
    """Tests for getting repositories from filled database."""
    route = ROUTES['repositories']
    param_choices = PARAM_CHOICES['repositories']

    def fill_db(self):
        """Fill database. Called in setUp."""
        db_session = database.session()
        rpm_repositories = [
            rpm_db_models.RPMRepository(id=1, path='1'),
            rpm_db_models.RPMRepository(id=2, path='2'),
            rpm_db_models.RPMRepository(id=3, path='3'),
            rpm_db_models.RPMRepository(id=4, path='4'),
            rpm_db_models.RPMRepository(id=5, path='5'),
        ]
        db_session.add_all(rpm_repositories)
        db_session.commit()
        db_session.close()

    # Expected result for request without any parameters.
    expected = [
        {'id': 1, 'path': '1'},
        {'id': 2, 'path': '2'},
        {'id': 3, 'path': '3'},
        {'id': 4, 'path': '4'},
        {'id': 5, 'path': '5'},
    ]

    # Tuples of query parameters and corresponding expected result.
    tuples_params_results = [
        ({}, expected),
        ({'id': '2'}, [expected[1]]),
        ({'path': '4'}, [expected[3]]),
        ({'limit': '3'}, [expected[0], expected[1], expected[2]]),
        ({'offset': '3'}, [expected[3], expected[4]]),
        ({'id': '4', 'path': '4'}, [expected[3]]),
    ]

class RESTTestRpmdiffCommentsFilled(RESTTestListsFilled):
    """Tests for getting comments from filled database."""
    route = ROUTES['comments']
    param_choices = PARAM_CHOICES['comments']

    def fill_db(self):
        """Fill database. Called in setUp."""
        db_session = database.session()
        users = [database.User.add(db_session, 'openid1', 'username1')]
        comparison_types = [database.ComparisonType(id=1, name='rpmdiff')]
        comparisons = [
            database.Comparison(
                id=1, state=0, time=datetime(1000, 1, 1), comparison_type_id=1
            ),
        ]
        rpm_repositories = [
            rpm_db_models.RPMRepository(id=1, path='repo1'),
        ]
        rpm_packages = [
            rpm_db_models.RPMPackage(
                id=1,
                name='name1',
                arch='arch1',
                epoch='epoch1',
                version='version1',
                release='release1',
                id_repo=1
            ),
        ]
        rpm_comparisons = [
            rpm_db_models.RPMComparison(
                id=1, id_group=1, pkg1_id=1, pkg2_id=1, state=0
            ),
            rpm_db_models.RPMComparison(
                id=2, id_group=1, pkg1_id=1, pkg2_id=1, state=1
            ),
        ]
        rpm_differences = [
            rpm_db_models.RPMDifference(
                id=1, id_comp=1, category=0, diff_type=0,
                diff_info='diff_info1', diff='diff1', state=0, waived=False,
            ),
            rpm_db_models.RPMDifference(
                id=2, id_comp=2, category=1, diff_type=1,
                diff_info='diff_info2', diff='diff2', state=1, waived=True,
            ),
        ]
        rpm_comments = [
            rpm_db_models.RPMComment(
                id=1,
                time=datetime(2018, 1, 1),
                text='text1',
                id_user='openid1',
                id_comp=None,
                id_diff=None,
            ),
            rpm_db_models.RPMComment(
                id=2,
                time=datetime(1000, 1, 1),
                text='text2',
                id_user='openid1',
                id_comp=1,
                id_diff=None,
            ),
            rpm_db_models.RPMComment(
                id=3,
                time=datetime(2018, 1, 1),
                text='text3',
                id_user='openid1',
                id_comp=2,
                id_diff=None,
            ),
            rpm_db_models.RPMComment(
                id=4,
                time=datetime(2000, 1, 1),
                text='text4',
                id_user='openid1',
                id_comp=None,
                id_diff=1,
            ),
            rpm_db_models.RPMComment(
                id=5,
                time=datetime(2018, 1, 1),
                text='text5',
                id_user='openid1',
                id_comp=None,
                id_diff=2,
            )
        ]
        db_session.add_all(users)
        db_session.add_all(comparison_types)
        db_session.add_all(comparisons)
        db_session.add_all(rpm_repositories)
        db_session.add_all(rpm_packages)
        db_session.add_all(rpm_comparisons)
        db_session.add_all(rpm_differences)
        db_session.add_all(rpm_comments)
        db_session.commit()
        db_session.close()

    # Expected result for request without any parameters.
    expected = [
        {
            'id': 1,
            'text': 'text1',
            'time': '2018-01-01 00:00:00',
            'username': 'username1',
        },
        {
            'id': 2,
            'text': 'text2',
            'time': '1000-01-01 00:00:00',
            'username': 'username1',
            'comparison': {
                'id': 1,
                'state': constants.STATE_STRINGS[0],
            }
        },
        {
            'id': 3,
            'text': 'text3',
            'time': '2018-01-01 00:00:00',
            'username': 'username1',
            'comparison': {
                'id': 2,
                'state': constants.STATE_STRINGS[1],
            }
        },
        {
            'id': 4,
            'text': 'text4',
            'time': '2000-01-01 00:00:00',
            'username': 'username1',
            'difference': {
                'id': 1,
                'category': constants.CATEGORY_STRINGS[0],
                'diff': 'diff1',
                'diff_info': 'diff_info1',
                'diff_type': constants.DIFF_TYPE_STRINGS[0],
                'state': constants.DIFF_STATE_STRINGS[0],
                'waived': False,
            }
        },
        {
            'id': 5,
            'text': 'text5',
            'time': '2018-01-01 00:00:00',
            'username': 'username1',
            'difference': {
                'id': 2,
                'category': constants.CATEGORY_STRINGS[1],
                'diff': 'diff2',
                'diff_info': 'diff_info2',
                'diff_type': constants.DIFF_TYPE_STRINGS[1],
                'state': constants.DIFF_STATE_STRINGS[1],
                'waived': True,
            }
        },
    ]

    # Tuples of query parameters and corresponding expected result.
    tuples_params_results = [
        ({}, expected),
        ({'id': '2'}, [expected[1]]),
        ({'comparison_id': '2'}, [expected[2]]),
        ({'comparison_state': constants.STATE_STRINGS[0]}, [expected[1]]),
        ({'difference_id': '2'}, [expected[4]]),
        ({'difference_category': constants.CATEGORY_STRINGS[1]}, [expected[4]]),
        ({'difference_diff': 'diff1'}, [expected[3]]),
        ({'difference_diff_type': constants.DIFF_TYPE_STRINGS[1]}, [expected[4]]),
        ({'difference_diff_info': 'diff_info2'}, [expected[4]]),
        ({'difference_state': constants.DIFF_STATE_STRINGS[0]}, [expected[3]]),
        ({'difference_waived': 'true'}, [expected[4]]),
        ({'limit': '2'}, [expected[0], expected[1]]),
        ({'offset': '3'}, [expected[3], expected[4]]),
    ]
