# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 10:56:53 2017

@author: pavla
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import UniqueConstraint
from ... import database

class BaseExported(object):
    to_export = []

    def exported(self, overwrite=None):
        if overwrite is None:
            overwrite = self.to_export
        return {k:v for k, v in vars(self).items() if k in overwrite}

class RPMComparison(BaseExported, database.Base):
    __tablename__ = 'rpm_comparisons'

    to_export = ['id_comp', 'state']

    id_comp = Column(
        Integer, ForeignKey('comparisons.id'), primary_key=True, nullable=False
    )
    pkg1_id = Column(Integer, ForeignKey('rpm_packages.id'), nullable=False)
    pkg2_id = Column(Integer, ForeignKey('rpm_packages.id'), nullable=False)
    state = Column(Integer, nullable=False)

    rpm_differences = relationship(
        "RPMDifference", back_populates="rpm_comparison"
    )
    rpm_package1 = relationship(
        "RPMPackage", foreign_keys=[pkg1_id], back_populates="rpm_comparisons1"
    )
    rpm_package2 = relationship(
        "RPMPackage", foreign_keys=[pkg2_id], back_populates="rpm_comparisons2"
    )

    comparison = relationship(
        "Comparison",
        backref=backref("rpm_comparison", uselist=False)
    )

    def __repr__(self):
        return ("<Comparison(id_comp='%s', pkg1_id='%s', pkg2_id='%s', "
                "state='%s')>") % (
                    self.id_comp,
                    self.pkg1_id,
                    self.pkg2_id,
                    self.state,
                )

class RPMDifference(BaseExported, database.Base):
    __tablename__ = 'rpm_differences'

    to_export = ['id', 'category', 'diff_type', 'diff_info', 'diff']

    id = Column(Integer, primary_key=True, nullable=False)
    id_comp = Column(
        Integer, ForeignKey('rpm_comparisons.id_comp'), nullable=False
    )
    category = Column(Integer)
    diff_type = Column(Integer, nullable=False)
    diff_info = Column(String)
    diff = Column(String, nullable=False)

    rpm_comparison = relationship(
        "RPMComparison", back_populates="rpm_differences"
    )

    def __repr__(self):
        return ("<Difference(id='%s', id_comp='%s', category='%s', "
                "diff_type='%s', diff_info='%s', diff='%s')>") % (
                    self.id,
                    self.id_comp,
                    self.category,
                    self.diff_type,
                    self.diff_info,
                    self.diff,
                )

class RPMPackage(BaseExported, database.Base):
    __tablename__ = 'rpm_packages'
    
    to_export = ['id', 'name', 'arch', 'epoch', 'version', 'release']

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    arch = Column(String, nullable=False)
    epoch = Column(String, nullable=False)
    version = Column(String, nullable=False)
    release = Column(String, nullable=False)
    id_repo = Column(
        Integer, ForeignKey('rpm_repositories.id'), nullable=False
    )

    UniqueConstraint('name', 'arch', 'epoch', 'version', 'release', 'id_repo')

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
        return ("<Package(id='%s', name='%s', arch='%s', epoch='%s', "
                "version='%s', release='%s', id_repo='%s')>") % (
                    self.id,
                    self.name,
                    self.arch,
                    self.epoch,
                    self.version,
                    self.release,
                    self.id_repo,
                )

    def rpm_filename(self):
        """Get RPM filename based on the package atributes.

        :param package dnf.package.Package: corresponds to an RPM file
        :return: RPM filename string
        """
        return '{name}-{version}-{release}.{arch}.rpm'.format(
            name=self.name,
            version=self.version,
            release=self.release,
            arch=self.arch,
        )

class RPMRepository(BaseExported, database.Base):
    __tablename__ = 'rpm_repositories'

    to_export = ['id', 'path']

    id = Column(Integer, primary_key=True, nullable=False)
    path = Column(String, nullable=False, unique=True)

    rpm_package = relationship(
        "RPMPackage", back_populates="rpm_repository"
    )

    def __repr__(self):
        return "<RPMRepository(id='%s', path='%s')>" % (self.id, self.path)
