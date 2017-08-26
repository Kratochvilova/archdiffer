# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 22:45:06 2017

@author: pavla
"""

import os
import configparser

config = configparser.ConfigParser()
config.read(os.environ.get('ARCHDIFFER_CONFIG', '/etc/archdiffer.conf'))

# TODO: solve problem: if required thing is not in config
