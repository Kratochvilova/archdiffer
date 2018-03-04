#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 09:27:50 2018

@author: pavla
"""

STATE_NEW = 0
STATE_DONE = 1
STATE_ERROR = -1
STATE_STRINGS = {
    STATE_NEW: 'new',
    'new': STATE_NEW,
    STATE_DONE: 'done',
    'done': STATE_DONE,
    STATE_ERROR: 'error',
    'error': STATE_ERROR,
}
