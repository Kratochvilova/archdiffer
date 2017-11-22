# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 12:32:32 2017

@author: pavla
"""

import subprocess
import dnf
from sqlalchemy.exc import IntegrityError
from .... import database
from ..rpm_db_models import (RPMComparison, RPMDifference, RPMPackage,
                             RPMRepository)
from ....backend.celery_app import celery_app

PLUGIN = 'rpmdiff'

TAGS = ('NAME', 'SUMMARY', 'DESCRIPTION', 'GROUP', 'LICENSE', 'URL',
        'PREIN', 'POSTIN', 'PREUN', 'POSTUN', 'PRETRANS', 'POSTTRANS')

PRCO = ('REQUIRES', 'PROVIDES', 'CONFLICTS', 'OBSOLETES',
        'RECOMMENDS', 'SUGGESTS', 'ENHANCES', 'SUPPLEMENTS')

def update_status(status):
    pass

def repository(session, repo_path):
    """Get repository from the database; create new record if none exists.

    :param session: session for communication with the database
    :type session: qlalchemy.orm.session.Session
    :param repo_path string: repository baseurl
    :return: repository
    :rtype: rpm_db_models.RPMRepository
    """
    try:
        repo = RPMRepository(path=repo_path)
        session.add(repo)
        session.commit()
    except IntegrityError:
        session.rollback()
        repo = session.query(RPMRepository).filter_by(path=repo_path).one()

    return repo

def package(session, pkg, repo_path):
    """Get package from the database; create new record if none exists.

    :param session: session for communication with the database
    :type session: qlalchemy.orm.session.Session
    :param package dnf.package.Package: corresponds to an RPM file
    :param repo_path string: repository baseurl
    :return: package
    :rtype: rpm_db_models.RPMPackage
    """
    id_repo = repository(session, repo_path).id

    try:
        rpm_package = RPMPackage(
            name=pkg.name,
            arch=pkg.arch,
            epoch=pkg.epoch,
            version=pkg.version,
            release=pkg.release,
            id_repo=id_repo
        )
        session.add(rpm_package)
        session.commit()
    except IntegrityError:
        session.rollback()
        rpm_package = session.query(RPMPackage).filter_by(
            name=pkg.name,
            arch=pkg.arch,
            epoch=pkg.epoch,
            version=pkg.version,
            release=pkg.release,
            id_repo=id_repo
        ).one()

    return rpm_package

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
    return subprocess.run(["rpmdiff", pkg1, pkg2], stdout=subprocess.PIPE)

def parse_rpmdiff(rpmdiff_output):
    diffs = []
    lines = rpmdiff_output.split('\n')
    for line in lines:
        if line != '':
            diffs.append(line.split(maxsplit=1))
    return diffs

def proces_differences(session, id_comp, pkg1, pkg2, diffs):
    errors = []
    for diff in diffs:
        if len(diff) != 2:
            errors.append(diff)
            continue

        if diff[1] in TAGS:
            difference = RPMDifference(
                id_comp=int(id_comp),
                category='tags',
                diff_type=diff[0],
                diff=diff[1]
            )
        elif diff[1].startswith(PRCO):
            difference = RPMDifference(
                id_comp=int(id_comp),
                category='PRCO',
                diff_type=diff[0],
                diff=diff[1]
            )
        else:
            difference = RPMDifference(
                id_comp=int(id_comp),
                category='files',
                diff_type=diff[0],
                diff=diff[1]
            )
        session.add(difference)
        session.commit()

    print('Unrecognized line in rpmdiff output:')
    for e in errors:
        print(e)

@celery_app.task(name='rpmdiff.compare')
def compare(pkg1, pkg2):
    session = database.session()

    # Download packages
    dnf_package1 = download_package(pkg1)
    dnf_package2 = download_package(pkg2)
    if dnf_package1 is None or dnf_package2 is None:
        return

    # Add packages to the database
    db_package1 = package(session, dnf_package1, pkg1['repository'])
    db_package2 = package(session, dnf_package2, pkg2['repository'])

    # Add comparison and rpm_comparison to the database
    comparison = database.Comparison()
    comparison.plugin = session.query(database.Plugin).filter_by(
        name=PLUGIN
    ).one()
    comparison.rpm_comparison = RPMComparison(
        id_comp=comparison.id,
        pkg1_id=db_package1.id,
        pkg2_id=db_package2.id,
        state='done',
    )
    session.add(comparison)
    session.commit()

    # Compare packages
    completed_process = run_rpmdiff(
        db_package1.rpm_filename(),
        db_package2.rpm_filename()
    )
    rpmdiff_output = completed_process.stdout.decode('UTF-8')
    diffs = parse_rpmdiff(rpmdiff_output)

    # Process results
    proces_differences(
        session,
        comparison.id,
        dnf_package1,
        dnf_package2,
        diffs
    )
