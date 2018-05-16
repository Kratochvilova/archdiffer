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
from .. import database

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

    def deep_sort(self, response):
        """Order all lists in the response.

        :param list response: response
        :return list: ordered response
        """
        if type(response) == list:
            response = sorted(response, key=lambda k: k['id'])
            new_response = []
            for item in response:
                new_response.append(self.deep_sort(item))
        elif type(response) == dict:
            for key, value in response.items():
                response[key] = self.deep_sort(value)
        return response

    def assert_response(self, expected):
        """Assert that response is as expected, aside from lists ordering.

        :param list expected: expected response
        """
        self.assertEqual(
            self.deep_sort(self.response), self.deep_sort(expected)
        )

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
        self.assert_response([])

    def test_basic_one(self):
        """Test getting instance - with no params set."""
        self.form_request_one()
        self.assert_code_ok()
        self.assert_response([])

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

class RESTTestComparisonsEmpty(RESTTestListsEmpty):
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

class RESTTestComparisonTypesEmpty(RESTTestListsEmpty):
    """Tests for getting comparison types from empty database."""
    route = 'rest/comparison_types'
    param_choices = {
        'id': IDS,
        'name': [''],
        'limit': LIMITS,
        'offset': OFFSETS,
    }

class RESTTestListsFilled(RESTTestLists):
    """Tests for getting lists from filled database. Abstract."""
    def run(self, result=None):
        """Overriden run so that it doesn't run these tests on this class."""
        if type(self) == RESTTestListsFilled:
            return result
        return super().run(result)

    def test_params(self):
        """Run test for each of the tuples_params_results. Check that with
        given parameters the response is as expected."""
        for params, expected in self.tuples_params_results:
            with self.subTest(**params):
                self.params = params
                self.form_request()
                self.assert_code_ok()
                self.assert_response(expected)

class RESTTestComparisonsFilled(RESTTestListsFilled):
    """Tests for getting comparisons from filled database."""
    route = RESTTestComparisonsEmpty.route
    param_choices = RESTTestComparisonsEmpty.param_choices

    def fill_db(self):
        """Fill database. Called in setUp."""
        db_session = database.session()
        comparison_types = [
            database.ComparisonType(id=1, name='1'),
            database.ComparisonType(id=2, name='2'),
        ]
        comparisons = [
            database.Comparison(
                id=1, state=1, time=datetime(9999, 1, 1), comparison_type_id=1
            ),
            database.Comparison(
                id=2, state=0, time=datetime(1000, 1, 1), comparison_type_id=2
            ),
            database.Comparison(
                id=3, state=0, time=datetime(2018, 1, 1), comparison_type_id=1
            ),
            database.Comparison(
                id=4, state=1, time=datetime(2018, 3, 1), comparison_type_id=1
            ),
        ]
        db_session.add_all(comparison_types)
        db_session.add_all(comparisons)
        db_session.commit()
        db_session.close()

    # Expected result for request without any parameters.
    expected = [
        {
            'id': 1,
            'state': STATE_STRINGS[1],
            'time': '9999-01-01 00:00:00',
            'comparison_type': {
                'id': 1,
                'name': '1',
            },
        },
        {
            'id': 2,
            'state': STATE_STRINGS[0],
            'time': '1000-01-01 00:00:00',
            'comparison_type': {
                'id': 2,
                'name': '2',
            },
        },
        {
            'id': 3,
            'state': STATE_STRINGS[0],
            'time': '2018-01-01 00:00:00',
            'comparison_type': {
                'id': 1,
                'name': '1',
            },
        },
        {
            'id': 4,
            'state': STATE_STRINGS[1],
            'time': '2018-03-01 00:00:00',
            'comparison_type': {
                'id': 1,
                'name': '1',
            },
        },
    ]

    # Tuples of query parameters and corresponding expected result.
    tuples_params_results = [
        ({}, expected),
        ({'id': '2'}, [expected[1]]),
        ({'state': STATE_STRINGS[0]}, [expected[1], expected[2]]),
        ({'before': '2018-02-01 00:00:00'}, [expected[1], expected[2]]),
        ({'after': '2018-02-01 00:00:00'}, [expected[0], expected[3]]),
        ({'comparison_type_id': '1'}, [expected[0], expected[2], expected[3]]),
        ({'comparison_type_name': '2'}, [expected[1]]),
        ({'limit': '2'}, [expected[0], expected[1]]),
        ({'offset': '3'}, [expected[3]]),
        (
            {
                'comparison_type_id': '1',
                'state': STATE_STRINGS[1],
                'after': '2017-01-01 00:00:00',
            },
            [expected[0], expected[3]]
        ),
    ]

class RESTTestComparisonTypesFilled(RESTTestListsFilled):
    """Tests for getting comparison types from filled database."""
    route = RESTTestComparisonTypesEmpty.route
    param_choices = RESTTestComparisonTypesEmpty.param_choices

    def fill_db(self):
        """Fill database. Called in setUp."""
        db_session = database.session()
        comparison_types = [
            database.ComparisonType(id=1, name='1'),
            database.ComparisonType(id=2, name='2'),
            database.ComparisonType(id=3, name='3'),
            database.ComparisonType(id=4, name='4'),
            database.ComparisonType(id=5, name='5'),
        ]
        db_session.add_all(comparison_types)
        db_session.commit()
        db_session.close()

    # Expected result for request without any parameters.
    expected = [
        {'id': 1, 'name': '1'},
        {'id': 2, 'name': '2'},
        {'id': 3, 'name': '3'},
        {'id': 4, 'name': '4'},
        {'id': 5, 'name': '5'},
    ]

    # Tuples of query parameters and corresponding expected result.
    tuples_params_results = [
        ({}, expected),
        ({'id': '2'}, [expected[1]]),
        ({'name': '4'}, [expected[3]]),
        ({'limit': '3'}, [expected[0], expected[1], expected[2]]),
        ({'offset': '3'}, [expected[3], expected[4]]),
        ({'id': '4', 'name': '4'}, [expected[3]]),
    ]
