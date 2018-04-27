#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Tue Feb 20 09:27:50 2018

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

# Codes for states of comparisons used in the database
STATE_NEW = 0
STATE_DONE = 1
STATE_ERROR = -1
STATE_STRINGS = {
    STATE_NEW: 'new',
    STATE_DONE: 'done',
    STATE_ERROR: 'error',
}
