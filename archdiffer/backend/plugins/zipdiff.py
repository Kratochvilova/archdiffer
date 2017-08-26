# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 10:44:17 2017

@author: pavla
"""

import zipfile
import os.path
from .. import config

from ... import database

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

def compare(pkg1, pkg2):
    session = database.Session()
    comparison = database.Comparison(
        module='zip', pkg1=pkg1, pkg2=pkg2, state='new'
    )
    session.add(comparison)
    session.commit()
    only_zip1, only_zip2 = diff_zips(pkg1, pkg2)
    for item in only_zip1:
        difference = database.Difference(
            id_comp=comparison.id, pkg=pkg1, diff_type='+', diff=item
        )
        session.add(difference)
    for item in only_zip2:
        difference = database.Difference(
            id_comp=comparison.id, pkg=pkg2, diff_type='+', diff=item
        )
        session.add(difference)
    comparison.state = 'done'
    session.add(comparison)
    session.commit()
