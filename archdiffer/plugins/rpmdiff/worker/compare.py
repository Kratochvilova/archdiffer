# -*- coding: utf-8 -*-

# This file is part of Archdiffer and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Created on Mon Sep  4 12:32:32 2017

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

import os
from tempfile import mkdtemp
from shutil import rmtree
import subprocess
from collections import defaultdict
import dnf
import rpm
from celery.signals import worker_process_init, worker_process_shutdown
from .... import database
from ..rpm_db_models import (RPMComparison, RPMDifference, RPMPackage)
from .. import constants
from ....backend.celery_app import celery_app
from .... import constants as app_constants

@worker_process_init.connect()
def setup_tmps(**kwargs):
    """Make temporal directory to store downloaded packages and set current
    woring directory there."""
    tmpdir = mkdtemp()
    os.chdir(tmpdir)

@worker_process_shutdown.connect()
def cleanup_tmps(**kwargs):
    """Remove the temporal directory."""
    tmpdir = os.getcwd()
    os.chdir('/')
    rmtree(tmpdir)

def download_packages(pkg):
    """Download packages whose parameters match the arguments.

    :param dict pkg: dict containing package parameters
    :return list[dnf.package.Package]: packages
    """
    base = dnf.Base()

    # Add repository
    label = 'temp_repo_label'
    base.repos.add_new_repo(label, base.conf, baseurl=[pkg['repository']])
    base.repos[label].enable()
    # Set cache directory to the tmpdir. Otherwise it won't see any changes in
    # repository.
    base.conf.cachedir = '.'
    try:
        print('Loading repository: %s' % pkg['repository'])
        base.repos[label].load()
        print('Repository loaded.')
    except:
        print('Repository loading failed.')
        return []
    base.fill_sack(load_system_repo=False)

    # Query packages
    pkgs = base.sack.query().available().filter(name=pkg['name'])
    if pkg['arch'] != '' and pkg['arch'] and isinstance(pkg['arch'], str):
        pkgs = pkgs.filter(arch=pkg['arch'])
    if pkg['epoch'] != '' and isinstance(pkg['epoch'], int):
        pkgs = pkgs.filter(epoch=pkg['epoch'])
    if pkg['release'] != '' and isinstance(pkg['release'], str):
        pkgs = pkgs.filter(release=pkg['release'])
    if pkg['version'] != '' and isinstance(pkg['version'], str):
        pkgs = pkgs.filter(version=pkg['version'])

    # Download the package
    if pkgs:
        print('Started package download: %s' % pkgs[0].name)
        base.conf.destdir = os.getcwd()
        base.repos.all().pkgdir = base.conf.destdir
        base.download_packages(list(pkgs))
        print('Finished package download: %s' % pkgs[0].name)

    return list(pkgs)

def group_by_arch(pkgs):
    """Make dict of groups of packagase sorted by the architectures.

    :param list[dnf.package.Package] pkgs: packages
    :return dict: dict of groups
    """
    arch_groups = defaultdict(list)
    for pkg in pkgs:
        arch_groups[pkg.arch].append(pkg)
    return arch_groups

def remove_old_versions(pkgs):
    """Remove older packages for each architecture.

    :param list[dnf.package.Package] pkgs: packages
    :return list[dnf.package.Package]: new list of packages
    """
    arch_groups = defaultdict(list)
    for pkg in pkgs:
        arch_groups[pkg.arch].append(pkg)

    pkg_list = []
    for key in arch_groups.keys():
        newest_label = None
        newest_pkg = None
        for pkg in arch_groups[key]:
            pkg_label = (str(pkg.epoch), str(pkg.version), str(pkg.release))
            if newest_label is None or rpm.labelCompare(newest_label, pkg_label):
                newest_label = pkg_label
                newest_pkg = pkg
        pkg_list.append(newest_pkg)

    return pkg_list

def make_tuples(original1, original2, pkgs1, pkgs2):
    """Make list of tuples from two lists of packages.

    :param dict original1: dict describing original request for first package
    :param dict original2: dict describing original request for second package
    :param list[dnf.package.Package] pkgs1: first list of packages
    :param list[dnf.package.Package] pkgs2: second list of packages
    :return list: list of package tuples
    """
    tuples = []

    pkgs1 = remove_old_versions(pkgs1)
    pkgs2 = remove_old_versions(pkgs2)

    for pkg1 in pkgs1:
        for pkg2 in pkgs2:
            if pkg1.arch == pkg2.arch:
                tuples.append((pkg1, pkg2))
    if tuples == []:
        for pkg1 in pkgs1:
            for pkg2 in pkgs2:
                tuples.append((pkg1, pkg2))
    return tuples

def run_rpmdiff(pkg1, pkg2):
    """Run rpmdiff as subprocess.

    :param string pkg1: name of the first package
    :param string pkg2: name of the second package
    :return: CompletedProcess instance
    """
    pkg1 = os.path.join(os.getcwd(), pkg1)
    pkg2 = os.path.join(os.getcwd(), pkg2)
    return subprocess.run(["rpmdiff", pkg1, pkg2], stdout=subprocess.PIPE)

def parse_rpmdiff(rpmdiff_output):
    """Parse output from rpmdiff.

    :param string rpmdiff_output: rpmdiff output
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
    :param int id_comp: id_comp of the corresponding RPMComparison
    :param list diffs: list of parsed differences from rpmdiff output
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
def compare(comp_id, pkg1, pkg2):
    """Compare two packages and write results to the database.

    :param int comp_id: id of Comparison which will be used as group
    :param dict pkg1: first package dict with keys:
        name, arch, epoch, version, release, repository
    :param dict pkg2: second package dict
    """
    session = database.session()

    # Download packages
    dnf_packages1 = download_packages(pkg1)
    dnf_packages2 = download_packages(pkg2)

    tuples = make_tuples(pkg1, pkg2, dnf_packages1, dnf_packages2)

    rpm_comparison = None
    for dnf_package1, dnf_package2 in tuples:
        # Add packages to the database
        db_package1 = RPMPackage.add(session, dnf_package1, pkg1['repository'])
        db_package2 = RPMPackage.add(session, dnf_package2, pkg2['repository'])

        # Add comparison and rpm_comparison to the database
        rpm_comparison = RPMComparison.add(
            session, db_package1, db_package2, id_group=comp_id
        )

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

    comp = session.query(database.Comparison).filter_by(id=comp_id).first()
    comp.update_state(session, app_constants.STATE_DONE)
