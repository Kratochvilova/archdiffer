# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 12:32:32 2017

@author: pavla
"""

import subprocess
import dnf
from .... import database
from ..rpm_db_models import (RPMComparison, RPMDifference, RPMPackage)
from .. import constants
from ....backend.celery_app import celery_app

def download_package(pkg):
    """Download package whose parameters match the arguments.

    :param pkg dict: dict containing package parameters
    :return: package or None
    """
    base = dnf.Base()

    # Add repository
    label = 'temp_repo_label'
    base.repos.add_new_repo(label, base.conf, baseurl=[pkg['repository']])
    base.repos[label].enable()
    try:
        base.repos[label].load()
    except:
        return None
    base.fill_sack()

    # Query packages
    pkgs = base.sack.query().available().filter(name=pkg['name'])
    if pkg['arch'] != '':
        pkgs = pkgs.filter(arch=pkg['arch'])
    if pkg['epoch'] != '':
        pkgs = pkgs.filter(epoch=pkg['epoch'])
    if pkg['release'] != '':
        pkgs = pkgs.filter(release=pkg['release'])
    if pkg['version'] != '':
        pkgs = pkgs.filter(version=pkg['version'])

    # Not allowing more than one package
    if len(pkgs) != 1:
        return None

    # Download the package
    print('Started package download: %s' % pkgs[0].name)
    base.conf.destdir = '.'
    base.repos.all().pkgdir = base.conf.destdir
    base.download_packages(list(pkgs))
    print('Finished package download: %s' % pkgs[0].name)

    return pkgs[0]

def run_rpmdiff(pkg1, pkg2):
    """Run rpmdiff as subprocess.

    :param pkg1 string: name of the first package
    :param pkg2 string: name of the second package
    :return: CompletedProcess instance
    """
    return subprocess.run(["rpmdiff", pkg1, pkg2], stdout=subprocess.PIPE)

def parse_rpmdiff(rpmdiff_output):
    """Parse output from rpmdiff.

    :param rpmdiff_output string: rpmdiff output
    :return list: list of diffs
    """
    diffs = []
    lines = rpmdiff_output.split('\n')
    for line in lines:
        if line != '':
            diffs.append(line.split(maxsplit=1))
    return diffs

def proces_differences(session, id_comp, differences):
    """Process differences from the rpmdiff output and add to the database.

    :param session: session for communication with the database
    :type session: qlalchemy.orm.session.Session
    :param id_comp integer: id_comp of the corresponding RPMComparison
    :param diffs list: list of parsed differences from rpmdiff output
    """
    # TODO: also check for renamed files
    # (diff_type='renamed', diff_info='name_of_new_file')
    bad_diffs = []
    category = ''
    diff_type = ''
    diff_info = ''

    for difference in differences:
        if len(difference) != 2:
            bad_diffs.append(difference)
            continue

        if difference[0] == 'removed':
            diff_type = constants.DIFF_TYPE_REMOVED
            diff_info = None
        elif difference[0] == 'added':
            diff_type = constants.DIFF_TYPE_ADDED
            diff_info = None
        else:
            diff_type = constants.DIFF_TYPE_CHANGED
            diff_info = difference[0]

        if difference[1] in constants.TAGS:
            category = constants.CATEGORY_TAGS
        elif difference[1].startswith(constants.PRCO):
            category = constants.CATEGORY_PRCO
        else:
            category = constants.CATEGORY_FILES

        RPMDifference.add(
            session, id_comp, category, diff_type, diff_info, difference[1]
        )

    if bad_diffs != []:
        print('Unrecognized lines in rpmdiff output:')
        for bad_diff in bad_diffs:
            print(bad_diff)

@celery_app.task(name='rpmdiff.compare')
def compare(pkg1, pkg2):
    """Compare two packages and write results to the database.

    :param pkg1 dict: first package dict with keys:
        name, arch, epoch, version, release, repository
    :param pkg2 dict: second package dict
    """
    session = database.session()

    # Download packages
    dnf_package1 = download_package(pkg1)
    dnf_package2 = download_package(pkg2)
    if dnf_package1 is None or dnf_package2 is None:
        return

    # Add packages to the database
    db_package1 = RPMPackage.add(session, dnf_package1, pkg1['repository'])
    db_package2 = RPMPackage.add(session, dnf_package2, pkg2['repository'])

    # Add comparison and rpm_comparison to the database
    rpm_comparison = RPMComparison.add(session, db_package1, db_package2)

    # Compare packages
    completed_process = run_rpmdiff(
        dnf_package1.localPkg(), dnf_package2.localPkg()
    )
    rpmdiff_output = completed_process.stdout.decode('UTF-8')
    diffs = parse_rpmdiff(rpmdiff_output)

    # Process results
    proces_differences(session, int(rpm_comparison.id), diffs)

    # Update RPMComparison state
    rpm_comparison.update_state(session, constants.STATE_DONE)
