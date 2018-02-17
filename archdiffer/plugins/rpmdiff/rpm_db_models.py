# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 10:56:53 2017

@author: pavla
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref, aliased
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.exc import IntegrityError
from ... import database
from . import constants

class BaseExported(object):
    """For exporting attributes from the models."""
    to_export = []

    def exported(self, overwrite=None):
        """Export attributes.

        :param overwrite list: list of attribute strings to be exported instead
            of the default ones
        :return dict: {attribute string: attribute value}
        """
        if overwrite is None:
            overwrite = self.to_export
        return {k:v for k, v in vars(self).items() if k in overwrite}

class RPMComparison(BaseExported, database.Base):
    __tablename__ = 'rpm_comparisons'

    to_export = ['id', 'state']

    id = Column(
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
        return ("<Comparison(id='%s', pkg1_id='%s', pkg2_id='%s', "
                "state='%s')>") % (
                    self.id,
                    self.pkg1_id,
                    self.pkg2_id,
                    self.state,
                )

    def update_state(self, ses, state):
        """Update state of the RPMComparison.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param state int: new state
        """
        self.state = state
        ses.add(self)
        ses.commit()

    @staticmethod
    def add(ses, rpm_package1, rpm_package2):
        """Add new RPMComparison together with corresponding Comparison.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param rpm_package1 RPMPackage: first package
        :param rpm_package2 RPMPackage: second package
        :return RPMComparison: newly added RPMComparison
        """
        comparison = database.Comparison()
        comparison.comparison_type = ses.query(
            database.ComparisonType
        ).filter_by(name=constants.COMPARISON_TYPE).one()
        comparison.rpm_comparison = RPMComparison(
            id=comparison.id,
            pkg1_id=rpm_package1.id,
            pkg2_id=rpm_package2.id,
            state=constants.STATE_NEW,
        )
        ses.add(comparison)
        ses.commit()
        return comparison.rpm_comparison

class RPMDifference(BaseExported, database.Base):
    __tablename__ = 'rpm_differences'

    to_export = ['id', 'category', 'diff_type', 'diff_info', 'diff']

    id = Column(Integer, primary_key=True, nullable=False)
    id_comp = Column(
        Integer, ForeignKey('rpm_comparisons.id'), nullable=False
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

    @staticmethod
    def add(ses, id_comp, category, diff_type, diff_info, diff):
        """Add new RPMDifference.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param id_comp int: id of corresponding comparison
        :param category int: category
        :param diff_type int: diff type
        :param diff_info string: diff_info
        :param diff string: diff
        :return RPMDifference: newly added RPMDifference
        """
        difference = RPMDifference(
            id_comp=id_comp,
            category=category,
            diff_type=diff_type,
            diff_info=diff_info,
            diff=diff,
        )
        ses.add(difference)
        ses.commit()
        return difference

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

    UniqueConstraint(name, arch, epoch, version, release, id_repo)

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

    @staticmethod
    def add(ses, pkg, repo_path):
        """Add package to the database if it doesn't already exist.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param package dnf.package.Package: corresponds to an RPM file
        :param repo_path string: repository baseurl
        :return: package
        :rtype: rpm_db_models.RPMPackage
        """
        id_repo = RPMRepository.add(ses, repo_path).id

        try:
            rpm_package = RPMPackage(
                name=pkg.name,
                arch=pkg.arch,
                epoch=pkg.epoch,
                version=pkg.version,
                release=pkg.release,
                id_repo=id_repo
            )
            ses.add(rpm_package)
            ses.commit()
        except IntegrityError:
            ses.rollback()
            rpm_package = ses.query(RPMPackage).filter_by(
                name=pkg.name,
                arch=pkg.arch,
                epoch=pkg.epoch,
                version=pkg.version,
                release=pkg.release,
                id_repo=id_repo
            ).one()

        return rpm_package

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

    @staticmethod
    def add(ses, repo_path):
        """Add repository to the database if it doesn't already exist.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param repo_path string: repository baseurl
        :return: repository
        :rtype: rpm_db_models.RPMRepository
        """
        try:
            repo = RPMRepository(path=repo_path)
            ses.add(repo)
            ses.commit()
        except IntegrityError:
            ses.rollback()
            repo = ses.query(RPMRepository).filter_by(path=repo_path).one()
        return repo

def joined_query(ses, table=RPMComparison):
    """Query database tables jointly.

    :param table: table setting which tables to query
    :type table: one of (RPMDifference, RPMComparison, RPMPackage,
                         RPMRepository)
    :return sqlalchemy.orm.query.Query: resulting query object
    """
    tables = []
    conditions = []

    pkg1 = aliased(RPMPackage, name='pkg1')
    pkg2 = aliased(RPMPackage, name='pkg2')
    repo1 = aliased(RPMRepository, name='repo1')
    repo2 = aliased(RPMRepository, name='repo2')

    if table == RPMRepository:
        tables = [RPMRepository]
    if table == RPMPackage:
        tables = [RPMPackage, RPMRepository]
        conditions = [pkg1.id_repo == repo1.id]
    if table == RPMComparison or table == RPMDifference:
        tables = [RPMComparison, database.Comparison, pkg1, pkg2, repo1, repo2]
        conditions = [
            RPMComparison.id == database.Comparison.id,
            RPMComparison.pkg1_id == pkg1.id,
            RPMComparison.pkg2_id == pkg2.id,
            pkg1.id_repo == repo1.id,
            pkg2.id_repo == repo2.id,
        ]

    query = ses.query(*tables).filter(*conditions)

    if table == RPMDifference:
        query = query.add_entity(RPMDifference).outerjoin(
            RPMDifference, RPMDifference.id_comp == RPMComparison.id
        )

    return query

def iter_query_result(result, table=RPMComparison):
    """Process result of the joined query.

    :param table: table setting which tables were queried
    :type table: one of (RPMDifference, RPMComparison, RPMPackage,
                         RPMRepository)
    :return: iterator of resulting dict
    :rtype: Iterator[dict]
    """
    print(result)
    def get_id(line):
        """Get id based on table."""
        if table == RPMComparison or table == RPMDifference:
            return line.RPMComparison.id
        elif table == RPMPackage:
            return line.RPMPackage.id
        return line.id

    def parse_line(line):
        """Parse line based on table."""
        if table == RPMComparison or table == RPMDifference:
            result_dict = {
                'time': str(line.Comparison.time),
                'type': constants.COMPARISON_TYPE,
                'pkg1': line.pkg1.exported(),
                'pkg2': line.pkg2.exported(),
                'state': constants.STATE_STRINGS[line.RPMComparison.state],
            }
            result_dict['pkg1']['repo'] = line.repo1.exported()
            result_dict['pkg2']['repo'] = line.repo2.exported()
            result_dict['pkg1']['filename'] = line.pkg1.rpm_filename()
            result_dict['pkg2']['filename'] = line.pkg2.rpm_filename()
        elif table == RPMPackage:
            result_dict = line.RPMPackage.exported()
            result_dict['repo'] = line.RPMRepository.exported()
            result_dict['filename'] = line.RPMPackage.rpm_filename()
        else:
            result_dict = {'path': line.path}

        return result_dict

    def get_difference(line):
        """Get difference from the line if table is RPMDifference"""
        if table != RPMDifference or line.RPMDifference is None:
            return
        diff = line.RPMDifference.exported()
        diff['category'] = constants.CATEGORY_STRINGS[diff['category']]
        diff['diff_type'] = constants.DIFF_TYPE_STRINGS[diff['diff_type']]
        return diff

    last_id = None
    result_dict = None
    differences = []

    for line in result:
        if last_id is None:
            # Save new id and comparison
            last_id = get_id(line)
            result_dict = parse_line(line)
        if get_id(line) != last_id:
            # Add all differences and yield
            if table == RPMDifference:
                result_dict['differences'] = differences
            yield (last_id, result_dict)
            # Save new id and comparison
            last_id = get_id(line)
            result_dict = parse_line(line)
            differences = []
        diff = get_difference(line)
        if diff is not None:
            differences.append(diff)
    # Add all differences and yield
    if table == RPMDifference:
        result_dict['differences'] = differences
    if last_id is not None:
        yield (last_id, result_dict)
