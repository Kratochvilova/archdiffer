# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 10:56:53 2017

@author: pavla
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from ... import database

class RPMComparison(database.Base):
    __tablename__ = 'rpm_comparisons'

    id_comp = Column(
        Integer, ForeignKey('comparisons.id'), primary_key=True, nullable=False
    )
    # time is set when commited
    time = Column(DateTime, default=func.now())
    pkg1_id = Column(Integer, ForeignKey('rpm_packages.id'), nullable=False)
    pkg2_id = Column(Integer, ForeignKey('rpm_packages.id'), nullable=False)
    state = Column(String, nullable=False)

    rpm_differences = relationship(
        "RPMDifference", back_populates="rpm_comparison"
    )
    rpm_package1 = relationship(
        "RPMPackage", foreign_keys=[pkg1_id], back_populates="rpm_comparisons1"
    )
    rpm_package2 = relationship(
        "RPMPackage", foreign_keys=[pkg2_id], back_populates="rpm_comparisons2"
    )    

    comparison = relationship("Comparison", backref="rpm_comparison")
    
    def __repr__(self):
        return "<Comparison(id_comp='%s', time='%s', pkg1_id='%s', pkg2_id='%s', state='%s')>" % (
        self.id_comp, self.time, self.pkg1_id, self.pkg2_id, self.state)

    def get_dict(self):
        comparison_dict = {
            'id_comp':self.id_comp,
            'time':self.time,
            'pkg1_id':self.pkg1_id,
            'pkg2_id':self.pkg2_id,
            'state':self.state
        }
        return comparison_dict

class RPMDifference(database.Base):
    __tablename__ = 'rpm_differences'

    id = Column(Integer, primary_key=True, nullable=False)
    id_comp = Column(
        Integer, ForeignKey('rpm_comparisons.id_comp'), nullable=False
    )
    pkg =  Column(String, nullable=False)
    diff_type = Column(String, nullable=False)
    diff = Column(String, nullable=False)

    rpm_comparison = relationship(
        "RPMComparison", back_populates="rpm_differences"
    )

    def __repr__(self):
        return "<Difference(id='%s', id_comp='%s', pkg='%s', diff_type='%s', diff='%s')>" % (
        self.id, self.id_comp, self.pkg, self.diff_type, self.diff)

    def get_dict(self):
        difference_dict = {
            'id':self.id,
            'id_comp':self.id_comp,
            'pkg':self.pkg,
            'diff_type':self.diff_type,
            'diff':self.diff
        }
        return difference_dict

class RPMPackage(database.Base):
    __tablename__ = 'rpm_packages'
    
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    arch = Column(String, nullable=False)
    epoch = Column(String, nullable=False)
    version = Column(String, nullable=False)
    release = Column(String, nullable=False)
    id_repo = Column(
        Integer, ForeignKey('rpm_repositories.id'), nullable=False
    )

    rpm_comparisons1 = relationship(
        "RPMComparison",
        foreign_keys='RPMComparison.pkg1_id',
        back_populates="rpm_package1"
    )
    rpm_comparisons2 = relationship(
        "RPMComparison",
        foreign_keys='RPMComparison.pkg2_id',
        back_populates="rpm_package2"
    )
    
    rpm_repository = relationship(
        "RPMRepository", back_populates="rpm_package"
    )

    def __repr__(self):
        return "<Package(id='%s', name='%s', arch='%s', epoch='%s', version='%s', release='%s', id_repo='%s')>" % (
        self.id, self.name, self.arch, self.epoch, self.version, self.release, self.id_repo)

    def get_dict(self):
        package_dict = {
            'id':self.id,
            'name':self.name,
            'arch':self.arch,
            'epoch':self.epoch,
            'version':self.version,
            'release':self.release,
            'id_repo':self.id_repo
        }
        return package_dict

    def rpm_filename(self):
        """Get RPM filename based on the package atributes.

        :param package dnf.package.Package: corresponds to an RPM file
        :return: RPM filename string
        """
        return '{name}-{version}-{release}.{arch}.rpm'.format(
            name=self.name,
            version=self.version,
            release=self.release,
            arch=self.arch
        )

class RPMRepository(database.Base):
    __tablename__ = 'rpm_repositories'

    id = Column(Integer, primary_key=True, nullable=False)
    path = Column(String, nullable=False)

    rpm_package = relationship(
        "RPMPackage", back_populates="rpm_repository"
    )

    def __repr__(self):
        return "<RPMRepository(id='%s', path='%s')>" % (self.id, self.path)

    def get_dict(self):
        repository_dict = {
            'id':self.id,
            'path':self.path
        }
        return repository_dict
