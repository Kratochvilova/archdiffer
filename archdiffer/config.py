# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Tue Aug 22 22:45:06 2017

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

import os
import configparser

config = configparser.ConfigParser()
config.read(os.environ.get('ARCHDIFFER_CONFIG', '/etc/archdiffer.conf'))
