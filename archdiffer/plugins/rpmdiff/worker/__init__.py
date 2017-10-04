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

MODULE = 'rpm'

def rpm_filename(package):
    return '{name}-{version}-{release}.{arch}.rpm'.format(
        name=package.name,
        version=package.version,
        release=package.release,
        arch=package.arch
    )

def update_status(status):
    pass

def download_packages(name, arch, epoch, release, version, repo_path):
    # Add repository
    # TODO: Label as repo_id with id from the database
    label = 'tmp_repo'
    base = dnf.Base()
    base.repos.add_new_repo(label, base.conf, baseurl=[repo_path])
    base.repos[label].enable()
    base.repos[label].load()
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
    print('Downloading package: %s' % rpm_filename(pkgs[0]))
    base.conf.destdir = '.'
    base.download_packages(list(pkgs))

    return pkgs[0]

def run_rpmdiff(pkg1, pkg2):
    return subprocess.run(["rpmdiff", pkg1, pkg2], stdout=subprocess.PIPE)

@celery_app.task(name='rpmdiff.compare')
def compare(pkg1, pkg2):
    # TODO: Add repos to the database if not already there

    # Download packages
    package1 = download_packages(
        pkg1['name'], pkg1['arch'], pkg1['epoch'],
        pkg1['release'], pkg1['version'], pkg1['repository']
    )
    package2 = download_packages(
        pkg2['name'], pkg2['arch'], pkg2['epoch'],
        pkg2['release'], pkg2['version'], pkg2['repository']
    )

    if package1 is None or package2 is None:
        return

    session = database.session()

    repo1 = session.query(rpm_db_models.RPMRepository).filter_by(path=pkg1['repository']).one_or_none()
    if repo1 is None:
        repo1 = rpm_db_models.RPMRepository(path=pkg1['repository'])
        session.add(repo1)
        session.commit()

    repo2 = session.query(rpm_db_models.RPMRepository).filter_by(path=pkg2['repository']).one_or_none()
    if repo2 is None:
        repo2 = rpm_db_models.RPMRepository(path=pkg2['repository'])
        session.add(repo2)
        session.commit()

    db_package1 = rpm_db_models.RPMPackage(
        name=package1.name, arch=package1.arch, epoch=package1.epoch,
        version=package1.version, release=package1.release,
    )
    db_package1.rpm_repository = repo1

    db_package2 = rpm_db_models.RPMPackage(
        name=package2.name, arch=package2.arch, epoch=package2.epoch,
        version=package2.version, release=package2.release
    )
    db_package2.rpm_repository = repo2
    
    session.add(db_package1)
    session.add(db_package2)
    session.commit()

    comparison = database.Comparison(module=MODULE)
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

    completed_process = run_rpmdiff(rpm_filename(package1), rpm_filename(package2))
    print(completed_process.stdout.decode('UTF-8'))

    
    # TODO: process results

