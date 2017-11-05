# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 12:32:32 2017

@author: pavla
"""

import dnf
import subprocess
from .... import database
from .. import rpm_db_models
from ....backend.celery_app import celery_app

PLUGIN = 'rpmdiff'

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
    rpm_repo = session.query(rpm_db_models.RPMRepository).filter_by(path=repo_path).one_or_none()
    if rpm_repo is None:
        rpm_repo = rpm_db_models.RPMRepository(path=repo_path)
        session.add(rpm_repo)
        session.commit()
    return rpm_repo

def package(session, package, repo_path):
    """Get package from the database; create new record if none exists.

    :param session: session for communication with the database
    :type session: qlalchemy.orm.session.Session
    :param package dnf.package.Package: corresponds to an RPM file
    :param repo_path string: repository baseurl
    :return: package
    :rtype: rpm_db_models.RPMPackage
    """
    id_repo = repository(session, repo_path).id
    rpm_package = session.query(rpm_db_models.RPMPackage).filter_by(
        name=package.name,
        arch=package.arch,
        epoch=package.epoch,
        version=package.version,
        release=package.release,
        id_repo=id_repo
    ).one_or_none()
    if rpm_package is None:
        rpm_package = rpm_db_models.RPMPackage(
            name=package.name,
            arch=package.arch,
            epoch=package.epoch,
            version=package.version,
            release=package.release,
            id_repo=id_repo
        )
        session.add(rpm_package)
        session.commit()
    return rpm_package

def download_packages(session, name, arch, epoch, release, version, repo_path):
    """Download packages whose parameters match the arguments.

    :param session: session for communication with the database
    :type session: qlalchemy.orm.session.Session
    :param name string: name of the package
    :param arch string: architecture of the package
    :param epoch string: epoch of the package
    :param release string: release of the package
    :param version string: version of the package
    :param repo_path string: repository baseurl
    :return: list of packages
    """
    base = dnf.Base()

    # Add repository
    label = 'temp_repo_label'
    base.repos.add_new_repo(label, base.conf, baseurl=[repo_path])
    base.repos[label].enable()
    try:
        base.repos[label].load()
    except:
        return None
    base.fill_sack()

    # Query packages
    pkgs = base.sack.query().available().filter(name=name)
    if arch != '':
        pkgs = pkgs.filter(arch=arch)
    if epoch != '':
        pkgs = pkgs.filter(epoch=epoch)
    if release != '':
        pkgs = pkgs.filter(release=release)
    if version != '':
        pkgs = pkgs.filter(version=version)

    # Not allowing more than one package
    if len(pkgs) != 1:
        return None

    # Download the package
    print('Downloading package: %s' % pkgs[0].name)
    base.conf.destdir = '.'
    base.repos.all().pkgdir = base.conf.destdir
    base.download_packages(list(pkgs))
    print('Download complete')

    return pkgs[0]

def run_rpmdiff(pkg1, pkg2):
    return subprocess.run(["rpmdiff", pkg1, pkg2], stdout=subprocess.PIPE)

def parse_rpmdiff(session, id_comp, pkg1, pkg2, rpmdiff_output):
    lines = rpmdiff_output.split('\n')
    for line in lines:
        try:
            left, right = line.split(maxsplit=1)
            difference = rpm_db_models.RPMDifference(
                id_comp=int(id_comp), pkg=str(pkg1), diff_type=left, diff=right
            )
            session.add(difference)
            session.commit()
        except:
            print(line)

@celery_app.task(name='rpmdiff.compare')
def compare(pkg1, pkg2):
    session = database.session()

    # Download packages
    package1 = download_packages(
        session, pkg1['name'], pkg1['arch'], pkg1['epoch'],
        pkg1['release'], pkg1['version'], pkg1['repository']
    )
    package2 = download_packages(
        session, pkg2['name'], pkg2['arch'], pkg2['epoch'],
        pkg2['release'], pkg2['version'], pkg2['repository']
    )
    if package1 is None or package2 is None:
        return

    # Add packages to the database
    db_package1 = package(session, package1, pkg1['repository'])
    db_package2 = package(session, package2, pkg2['repository'])

    # Add comparison and rpm_comparison to the database
    comparison = database.Comparison()
    comparison.plugin = session.query(database.Plugin).filter(database.Plugin.name==PLUGIN).one()
    comparison.rpm_comparison = [
        rpm_db_models.RPMComparison(
            id_comp = comparison.id,
            pkg1_id=db_package1.id,
            pkg2_id=db_package2.id,
            state='done'
        )
    ]

    session.add(comparison)
    session.commit()

    # Compare packages
    completed_process = run_rpmdiff(db_package1.rpm_filename(), db_package2.rpm_filename())
    rpmdiff_output = completed_process.stdout.decode('UTF-8')
    parse_rpmdiff(session, comparison.id, package1, package2, rpmdiff_output)

    # TODO: process results
