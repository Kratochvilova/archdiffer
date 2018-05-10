#!/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Tue Aug 15 20:58:38 2017

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>

"""
import sys
from archdiffer.flask_frontend import flask_app

port = 5000
if len(sys.argv) > 1:
    port = int(sys.argv[1])

flask_app.run(port=port)
