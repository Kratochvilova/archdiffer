#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 22:01:26 2018

@author: pavla
"""

# Name of the comparison_type implemented by this module
COMPARISON_TYPE = 'rpmdiff'

# Codes for states of rpm_comparisons
STATE_NEW = 0
STATE_DONE = 1
STATE_FILTERING = 2
STATE_STRINGS = {
    STATE_NEW: 'new',
    STATE_DONE: 'done',
    STATE_FILTERING: 'filtering',
}

# Codes for categories of rpm_differences
CATEGORY_TAGS = 0
CATEGORY_PRCO = 1
CATEGORY_FILES = 2
CATEGORY_STRINGS = {
    CATEGORY_TAGS: 'tags',
    CATEGORY_PRCO: 'dependencies',
    CATEGORY_FILES: 'files',
}

# Codes for types of rpm_differences
DIFF_TYPE_REMOVED = 0
DIFF_TYPE_ADDED = 1
DIFF_TYPE_CHANGED = 2
DIFF_TYPE_RENAMED = 3
DIFF_TYPE_STRINGS = {
    DIFF_TYPE_REMOVED: 'removed',
    DIFF_TYPE_ADDED: 'added',
    DIFF_TYPE_CHANGED: 'changed',
    DIFF_TYPE_RENAMED: 'renamed',
}

# Codes for states of rpm_differences
DIFF_STATE_IGNORED = 0
DIFF_STATE_NORMAL = 1
DIFF_STATE_ERROR = 2
DIFF_STATE_STRINGS = {
    DIFF_STATE_IGNORED: 'ignored',
    DIFF_STATE_NORMAL: 'normal',
    DIFF_STATE_ERROR: 'error',
}

# List of all tags appearing in the results of the external rpmdiff
TAGS = ('NAME', 'SUMMARY', 'DESCRIPTION', 'GROUP', 'LICENSE', 'URL',
        'PREIN', 'POSTIN', 'PREUN', 'POSTUN', 'PRETRANS', 'POSTTRANS')

# List of all dependency types appearing in the results of the external rpmdiff
PRCO = ('REQUIRES', 'PROVIDES', 'CONFLICTS', 'OBSOLETES',
        'RECOMMENDS', 'SUGGESTS', 'ENHANCES', 'SUPPLEMENTS')
