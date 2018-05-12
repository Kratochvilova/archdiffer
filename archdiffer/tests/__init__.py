#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Thu May 10 10:22:09 2018

@author: pavla
"""

import os
from tempfile import mkdtemp
from shutil import rmtree
import copy
import time
import subprocess
import unittest
import socket
import requests
import json
from .config import config
from . import database

_curdir = os.path.dirname(os.path.abspath(__file__))
_basedir = os.path.dirname(_curdir)
#_frontend_launcher = os.path.join(_basedir, 'debug_flask.py')
_frontend_launcher = 'debug_flask.py'

class RESTTest(unittest.TestCase):
    def update_configfile(self):
        """Update config with new database url and save to temporary test
        configfile.
        """
        # New database path
        self.database_path = os.path.join(self.tmpdir, 'test.db')
        self.database_url = 'sqlite:///%s' % self.database_path

        # Update config with database url
        config['common']['DATABASE_URL'] = self.database_url

        # New config file
        self.config_path = os.path.join(self.tmpdir, 'test.conf')
        with open(self.config_path, 'w') as configfile:
            config.write(configfile)

    def setUp(self):
        """Create new database with test user; run flask-frontend and backend.
        """
        # Make temporal directory to store database.
        self.tmpdir = mkdtemp()

        # Update config with database url
        self.update_configfile()

        # Initialize database
        database.Base.metadata.create_all(database.engine(force_new=True))

        # TODO: (optional) fill in database

        # Create user with api_login and api_token
        db_session = database.session()
        user = database.User.add(db_session, 'test_openid', 'test_username')
        user.new_token(
            db_session,
            size=int(config['web']['API_TOKEN_LENGTH']),
            token_expiration=int(config['web']['API_TOKEN_EXPIRATION']),
        )
        self.auth = (user.api_login, user.api_token)

        # Create env with ARCHDIFFER_CONFIG
        env = copy.copy(os.environ)
        env.update({'ARCHDIFFER_CONFIG': self.config_path})

        # Get random port for flask
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 0))
        port = sock.getsockname()[1]
        self.baseurl = 'http://127.0.0.1:%s/' % port
        sock.close()

        # Run frontend
        self.frontend = subprocess.Popen(
            ['python3', _frontend_launcher, str(port)],
            cwd=_basedir,
            env=env,
        )

        # Run backend
        self.backend = subprocess.Popen(
            ['python3', '-m', 'archdiffer.backend', 'worker', '-c', '1'],
            cwd=_basedir,
            env=env,
        )

        # Repeatedly try request to ensure the frontend started
        for i in range(0, 5):
            time.sleep(2**i)
            try:
                self.get('rest')
                break
            except requests.exceptions.ConnectionError:
                print('Waiting for flask to start.')

        print('setup')

    def get(self, route, params=None):
        """Send GET request and save response status code and data.

        :param string route: route to the source
        :param dict params: parameters to be passed in url
        """
        r = requests.get(self.baseurl + route, params=params)
        self.status_code = r.status_code
        try:
            self.response = r.json()
        except ValueError:
            self.response = None

    def post(self, route, data=None):
        """Send POST request and save response status code and data.

        :param string route: route to the source
        :param data: data of the request, will be jsonified
        """
        r = requests.post(
            self.baseurl + route, auth=self.auth, data=json.dumps(data),
        )
        self.status_code = r.status_code
        try:
            self.response = r.json()
        except ValueError:
            self.response = None

    def put(self, route, data=None):
        """Send PUT request and save response status code and data.

        :param string route: route to the source
        :param data: data of the request, will be jsonified
        """
        r = requests.put(
            self.baseurl + route, auth=self.auth, data=json.dumps(data),
        )
        self.status_code = r.status_code
        try:
            self.response = r.json()
        except ValueError:
            self.response = None

    def assert_code_eq(self, code):
        """Assert that response status code is equal to given code.

        :param int code: status code to compare to response
        """
        self.assertEqual(self.status_code, code)

    def assert_code_ok(self):
        """Assert that response status code is OK."""
        self.assert_code_eq(requests.codes.ok)

    def assert_response_emptylist(self):
        """Assert that response is empty list."""
        self.assertEqual(self.response, [])

    def tearDown(self):
        """Terminate flask-frontend and backend; remove temporal files."""
        # Terminate frontend
        self.frontend.terminate()
        self.frontend.wait()

        # Terminate backend
        self.backend.terminate()
        self.backend.wait()

        # Remove the temporal directory.
        rmtree(self.tmpdir)

        print('teardown')

if __name__ == '__main__':
    unittest.main()
