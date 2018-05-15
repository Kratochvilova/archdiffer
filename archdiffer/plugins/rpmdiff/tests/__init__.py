
# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Mon May  7 12:25:31 2018

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from datetime import datetime
from ....tests import RESTTest
from ....tests.tests_rest_routes import RESTTestListsEmpty
from .... import constants as app_constants
from .. import constants

DATETIMES = [
    datetime(2018, 1, 1),
    datetime(1, 1, 1),
    datetime(9999, 1, 1),
]

IDS = LIMITS = OFFSETS = [0, 1, 2, 10, 999999]

GROUP_STATES = list(app_constants.STATE_STRINGS.values())
STATES = list(constants.STATE_STRINGS.values())
CATEGORIES = list(constants.CATEGORY_STRINGS.values())
DIFF_TYPES = list(constants.DIFF_TYPE_STRINGS.values())
DIFF_STATES = list(constants.DIFF_STATE_STRINGS.values())

class RESTTestRpmdiffRoutes(RESTTest):
    """Tests for route 'rpmdiff/rest'."""
    expected_response = {
        "/rpmdiff/rest": {
            "methods": [
                "GET"
            ],
            "routes": {
                "/rpmdiff/rest/comments": {
                    "methods": [
                        "GET",
                        "POST",
                    ],
                    "routes": {
                        "/rpmdiff/rest/comments/<int:id>": {
                            "methods": [
                                "GET"
                            ],
                            "routes": {}
                        },
                        "/rpmdiff/rest/comments/by_comp/<int:id_comp>": {
                            "methods": [
                                "GET"
                            ],
                            "routes": {}
                        },
                        "/rpmdiff/rest/comments/by_diff/<int:id_diff>": {
                            "methods": [
                                "GET"
                            ],
                            "routes": {}
                        },
                        "/rpmdiff/rest/comments/by_user/<string:username>": {
                            "methods": [
                                "GET"
                            ],
                            "routes": {}
                        }
                    }
                },
                "/rpmdiff/rest/comparisons": {
                    "methods": [
                        "GET",
                        "POST"
                    ],
                    "routes": {
                        "/rpmdiff/rest/comparisons/<int:id>": {
                            "methods": [
                                "GET"
                            ],
                            "routes": {}
                        }
                    }
                },
                "/rpmdiff/rest/differences": {
                    "methods": [
                        "GET"
                    ],
                    "routes": {
                        "/rpmdiff/rest/differences/<int:id>": {
                            "methods": [
                                "GET",
                                "PUT"
                            ],
                            "routes": {}
                        }
                    }
                },
                "/rpmdiff/rest/groups": {
                    "methods": [
                        "GET"
                    ],
                    "routes": {
                        "/rpmdiff/rest/groups/<int:id>": {
                            "methods": [
                                "GET"
                            ],
                            "routes": {}
                        }
                    }
                },
                "/rpmdiff/rest/packages": {
                    "methods": [
                        "GET"
                    ],
                    "routes": {
                        "/rpmdiff/rest/packages/<int:id>": {
                            "methods": [
                                "GET"
                            ],
                            "routes": {}
                        }
                    }
                },
                "/rpmdiff/rest/repositories": {
                    "methods": [
                        "GET"
                    ],
                    "routes": {
                        "/rpmdiff/rest/repositories/<int:id>": {
                            "methods": [
                                "GET"
                            ],
                            "routes": {}
                        }
                    }
                }
            }
        }
    }

    def assert_response(self):
        """Asert that response is as expected."""
        self.assertEqual(self.response, self.expected_response)

    def test_get_routes(self):
        """Test GET method on 'rpmdiff/rest'."""
        self.maxDiff = None
        self.get('rpmdiff/rest')
        self.assert_code_ok()
        self.assert_response()

class RESTTestRpmdiffComparisons(RESTTestListsEmpty):
    """Tests for getting comparisons from empty database."""
    route = 'rpmdiff/rest/comparisons'

    param_choices = {
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
    }

class RESTTestRpmdiffGroups(RESTTestListsEmpty):
    """Tests for getting comparison groups from empty database."""
    route = 'rpmdiff/rest/groups'

    param_choices = {
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
    }

class RESTTestRpmdiffDifferences(RESTTestListsEmpty):
    """Tests for getting differences from empty database."""
    route = 'rpmdiff/rest/differences'

    param_choices = {
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
    }

class RESTTestRpmdiffPackages(RESTTestListsEmpty):
    """Tests for getting packages from empty database."""
    route = 'rpmdiff/rest/packages'

    param_choices = {
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
    }

class RESTTestRpmdiffRepositories(RESTTestListsEmpty):
    """Tests for getting repositories from empty database."""
    route = 'rpmdiff/rest/repositories'

    param_choices = {
        'id': IDS,
        'path': [''],
        'limit': LIMITS,
        'offset': OFFSETS,
    }

class RESTTestRpmdiffComments(RESTTestListsEmpty):
    """Tests for getting comments from empty database."""
    route = 'rpmdiff/rest/comments'

    param_choices = {
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
    }
