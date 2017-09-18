# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 12:32:32 2017

@author: pavla
"""

import dnf
from ... import database
from ...backend.celery_app import celery_app

MODULE = 'rpm'

def download_packages(name, arch, epoch, release, version, repo_path):
    # TODO: label as repo_path or its hash?
    label = 'tmp_repo'
    base = dnf.Base()
    base.repos.add_new_repo(label, base.conf, baseurl=[repo_path])
    base.repos[label].enable()
    base.repos[label].load()
    base.fill_sack()
    pkgs = base.sack.query().available().filter(name=name)
    if arch != '':
        pkgs = pkgs.filter(arch=arch)
    if epoch != '':
        pkgs = pkgs.filter(epoch=epoch)
    if release != '':
        pkgs = pkgs.filter(release=release)
    if version != '':
        pkgs = pkgs.filter(version=version)
    for p in pkgs:
        print(p.name)
        print(p.arch)
        print(p.epoch)
        print(p.release)
        print(p.version)
    base.conf.destdir = '.'
    base.download_packages(list(pkgs))

def run_rpmdiff(pkg1, pkg2):
    pass

@celery_app.task(name='rpmdiff.compare')
def compare(pkg1, pkg2):
    session = database.Session()
    package1 = database.RPMPackage(
        name=pkg1['name'], arch=pkg1['arch'], epoch=pkg1['epoch'],
        version=pkg1['version'], release=pkg1['release'],
        repository=pkg1['repository']
    )
    package2 = database.RPMPackage(
        name=pkg2['name'], arch=pkg2['arch'], epoch=pkg2['epoch'],
        version=pkg2['version'], release=pkg2['release'],
        repository=pkg2['repository']
    )
    session.add(package1)
    session.add(package2)
    session.commit()

    comparison = database.RPMComparison(
        module='rpm', pkg1=package1.id, state='new'
    )
    session.add(comparison)
    session.commit()

    download_packages(
        pkg1['name'], pkg1['arch'], pkg1['epoch'],
        pkg1['release'], pkg1['version'], pkg1['repository']
    )

    # TODO: compare packages and save results

    comparison.state = 'done'
    session.add(comparison)
    session.commit()
