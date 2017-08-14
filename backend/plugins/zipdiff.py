# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 10:44:17 2017

@author: pavla
"""

import zipfile
import os.path
from .. import config

MODULE = 'zip'

def diff_lists(list1, list2):
    """Gets difference between two lists.
    @param list1: first list
    @param list2: second list
    @return (elements only in list1, elements only in list2)
    """
    return (
        list(set(list1).difference(set(list2))),
        list(set(list2).difference(set(list1)))
    )

def diff_zips(name1, name2):
    """Gets difference between two zip files.
    @param name1: name of the first zip
    @param name2: name of the second zip
    @return (elements only in first zip, elements only in second zip)
    """
    path1 = os.path.join(config.EXAMPLES_PATH, name1)
    path2 = os.path.join(config.EXAMPLES_PATH, name2)
    zip1 = zipfile.ZipFile(path1, 'r')
    zip2 = zipfile.ZipFile(path2, 'r')
    result = diff_lists(zip1.namelist(), zip2.namelist())
    zip1.close()
    zip2.close()
    return result

def create_log(db, req_dict):
    """Creates log for one comparisons record,
    and sets state of the record as done.
    @param db: DatabaseConnection
    @param req_dict: dict for the comparisons record
    """
    only_zip1, only_zip2 = diff_zips(req_dict['data1'], req_dict['data2'])
    for item in only_zip1:
        db.insert_row_differences(req_dict['id'], req_dict['data1'], '+', item)
    for item in only_zip2:
        db.insert_row_differences(req_dict['id'], req_dict['data2'], '+', item)
    db.set_state(req_dict['id'], 'done')

def process_requests(db):
    """Gets all new requests for zip module, and processes them.
    @param db: DatabaseConnection
    """
    requests = db.get_requests(MODULE)
    for req in requests:
        req_dict = db.parse_row_comparisons(req)
        create_log(db, req_dict)

# TODO: compare function
def compare(db, pkg1, pkg2):
    return pkg1
