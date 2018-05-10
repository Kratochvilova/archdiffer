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

_curdir = os.path.dirname(os.path.abspath(__file__))
_basedir = os.path.dirname(_curdir)
#_frontend_launcher = os.path.join(_basedir, 'debug_flask.py')
_frontend_launcher = 'debug_flask.py'
#_config = os.path.join(_basedir, 'debug.conf')
_config = 'debug.conf'

class RESTTest(unittest.TestCase):
    def setUp(self):
        # Make temporal directory to store database.
        self.tmpdir = mkdtemp()
        # TODO: Create database
        # TODO: Initialize database
        # TODO: (optional) or fill database
        # TODO: create config
        # Create user with api_login and api_token
        self.api_login = self.api_token = 'foo'
        # Create env with ARCHDIFFER_CONFIG
        env = copy.copy(os.environ)
        env.update({'ARCHDIFFER_CONFIG': _config})
        # Get random port
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
            ['python3', '-m', 'archdiffer.backend', 'worker'],
            cwd=_basedir,
            env=env,
        )
        # TODO: instead of waiting, repeatedly try request on /
        time.sleep(5)
        print('setup')

    def get(self, route, params):
        r = requests.get(self.baseurl + route, params=params)
        self.status_code = r.status_code
        self.response = r.json()

    def push(self, route, data):
        r = requests.post(
            self.baseurl + route,
            auth=(self.api_login, self.api_token),
            data=json.dumps(data),
        )
        self.status_code = r.status_code
        self.response = r.json()

    def put(self, route, data):
        r = requests.put(
            self.baseurl + route,
            auth=(self.api_login, self.api_token),
            data=json.dumps(data),
        )
        self.status_code = r.status_code
        self.response = r.json()

    def tearDown(self):
        self.frontend.terminate()
        self.frontend.wait()
        self.backend.terminate()
        self.backend.wait()
        # Remove the temporal directory.
        rmtree(self.tmpdir)
        print('teardown')

class RESTTest1(RESTTest):
    def test_foo(self):
        self.assertEqual(0, 0)
        # self.assertEqual(r.status_code, requests.codes.ok)

    def test_foo2(self):
        self.assertEqual(0, 0)

if __name__ == '__main__':
    unittest.main()
