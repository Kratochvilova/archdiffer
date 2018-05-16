# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Sat May 12 20:39:46 2018

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from random import choice
from datetime import datetime
from . import RESTTest
from ..constants import STATE_STRINGS

DATETIMES = [
    '1000-01-01 00:00:00',
    '2018-01-01 00:00:00',
    '9999-01-01 00:00:00',
]

IDS = LIMITS = OFFSETS = ['0', '1', '2', '10', '999999']

STATES = list(STATE_STRINGS.values())

class RESTTestRoutes(RESTTest):
    """Tests for route 'rest'."""
    expected_response = {
        "/rest": {
            "methods": [
                "GET"
            ],
            "routes": {
                "/rest/comparison_types": {
                    "methods": [
                        "GET"
                    ],
                    "routes": {
                        "/rest/comparison_types/<int:id>": {
                            "methods": [
                                "GET"
                            ],
                            "routes": {}
                        }
                    }
                },
                "/rest/comparisons": {
                    "methods": [
                        "GET"
                    ],
                    "routes": {
                        "/rest/comparisons/<int:id>": {
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
        """Test GET method on 'rest'."""
        self.get('rest')
        self.assert_code_ok()
        self.assert_response()

class RESTTestLists(RESTTest):
    """For testing getting lists from the database."""
    route = None
    # Accepted query parameters (values are lists of tested values).
    param_choices = {}

    def setUp(self):
        super().setUp()
        self.params = {}

    def set_params(self, parameters):
        """Randomly set parameters based on the given list.

        :param list parameters: list of parameters to be set.
        """
        for param in self.param_choices:
            if param in parameters:
                self.params[param] = choice(self.param_choices[param])

    def form_request(self):
        """Form GET request based on route and parameters."""
        self.get(self.route, params=self.params)

    def form_request_one(self):
        """Form GET request for random item based on route and parameters."""
        self.get('%s/%s' % (self.route, choice(IDS)), params=self.params)

class RESTTestListsEmpty(RESTTestLists):
    """Tests for getting lists from empty database. Abstract."""
    def run(self, result=None):
        """Overriden run so that it doesn't run these tests on this class."""
        if type(self) == RESTTestListsEmpty:
            return result
        return super().run(result)

    def test_basic(self):
        """Test getting list - with no params set."""
        self.form_request()
        self.assert_code_ok()
        self.assert_response_emptylist()

    def test_basic_one(self):
        """Test getting instance - with no params set."""
        self.form_request_one()
        self.assert_code_ok()
        self.assert_response_emptylist()

    def test_individual_params(self):
        """Test getting list - for each param set individually."""
        for param in self.param_choices:
            with self.subTest(param=param):
                self.params = {}
                self.set_params([param])
                self.test_basic()

    def test_all_params(self):
        """Test getting list - for all params set."""
        self.params = {}
        self.set_params(self.param_choices)
        self.test_basic()

class RESTTestComparisons(RESTTestListsEmpty):
    """Tests for getting comparisons from empty database."""
    route = 'rest/comparisons'

    param_choices = {
        'id': IDS,
        'state': STATES,
        'before': DATETIMES,
        'after': DATETIMES,
        'comparison_type_id': IDS,
        'comparison_type_name': [''],
        'limit': LIMITS,
        'offset': OFFSETS,
    }

class RESTTestComparisonTypes(RESTTestListsEmpty):
    """Tests for getting comparison types from empty database."""
    route = 'rest/comparison_types'

    param_choices = {
        'id': IDS,
        'name': [''],
        'limit': LIMITS,
        'offset': OFFSETS,
    }
