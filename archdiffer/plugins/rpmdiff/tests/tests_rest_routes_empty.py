# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Thu May 17 13:20:29 2018

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from random import choice
from ....tests import RESTTest
from ....tests.tests_rest_routes import RESTTestListsEmpty, IDS
from .tests_rest_constants import ROUTES, PARAM_CHOICES

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
        self.get('rpmdiff/rest')
        self.assert_code_ok()
        self.assert_response()

class RESTTestRpmdiffComparisonsEmpty(RESTTestListsEmpty):
    """Tests for getting comparisons from empty database."""
    route = ROUTES['comparisons']
    param_choices = PARAM_CHOICES['comparisons']

class RESTTestRpmdiffGroupsEmpty(RESTTestListsEmpty):
    """Tests for getting comparison groups from empty database."""
    route = ROUTES['groups']
    param_choices = PARAM_CHOICES['groups']

class RESTTestRpmdiffDifferencesEmpty(RESTTestListsEmpty):
    """Tests for getting differences from empty database."""
    route = ROUTES['differences']
    param_choices = PARAM_CHOICES['differences']

class RESTTestRpmdiffPackagesEmpty(RESTTestListsEmpty):
    """Tests for getting packages from empty database."""
    route = ROUTES['packages']
    param_choices = PARAM_CHOICES['packages']

class RESTTestRpmdiffRepositoriesEmpty(RESTTestListsEmpty):
    """Tests for getting repositories from empty database."""
    route = ROUTES['repositories']
    param_choices = PARAM_CHOICES['repositories']

class RESTTestRpmdiffCommentsEmpty(RESTTestListsEmpty):
    """Tests for getting comments from empty database."""
    route = ROUTES['comments']
    param_choices = PARAM_CHOICES['comments']

    def test_by_comp_id(self):
        """Test getting instance by comparison id - with no params set."""
        self.get('%s/by_comp/%s' % (self.route, choice(IDS)))
        self.assert_code_ok()
        self.assert_response([])

    def test_by_diff_id(self):
        """Test getting instance by difference id - with no params set."""
        self.get('%s/by_diff/%s' % (self.route, choice(IDS)))
        self.assert_code_ok()
        self.assert_response([])

    def test_by_username(self):
        """Test getting instance by username - with no params set."""
        self.get('%s/by_user/%s' % (self.route, choice(['username1'])))
        self.assert_code_ok()
        self.assert_response([])
