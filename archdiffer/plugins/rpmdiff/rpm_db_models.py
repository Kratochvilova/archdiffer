# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 10:56:53 2017

@author: pavla
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref, aliased
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.exc import IntegrityError
from ... database import Base, Comparison, ComparisonType
from . import constants
from ... import constants as app_constants
from ...flask_frontend.database_tasks import modify_query

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

class RPMComparison(BaseExported, Base):
    __tablename__ = 'rpm_comparisons'

    to_export = ['id', 'id_group', 'state']

    id = Column(Integer, primary_key=True, nullable=False)
    id_group = Column(
        Integer, ForeignKey('comparisons.id'), nullable=False
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
        return ("<Comparison(id='%s', id_group='%s', pkg1_id='%s', "
                "pkg2_id='%s', state='%s')>") % (
                    self.id,
                    self.id_group,
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

    def update_group_state(self, ses, state):
        """Update state of the Comparison.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param state int: new state
        """
        self.comparison.state = state
        ses.add(self.comparison)
        ses.commit()

    @staticmethod
    def add(ses, rpm_package1, rpm_package2, id_group=None):
        """Add new RPMComparison together with corresponding Comparison.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param rpm_package1 RPMPackage: first package
        :param rpm_package2 RPMPackage: second package
        :return RPMComparison: newly added RPMComparison
        """
        if id_group is None:
            comparison_type_id = ses.query(ComparisonType).filter_by(
                name=constants.COMPARISON_TYPE
            ).one().id
            comparison = Comparison.add(ses, comparison_type_id)
            id_group = comparison.id

        rpm_comparison = RPMComparison(
            id_group = id_group,
            pkg1_id=rpm_package1.id,
            pkg2_id=rpm_package2.id,
            state=constants.STATE_NEW,
        )
        ses.add(rpm_comparison)
        ses.commit()
        return rpm_comparison

    @staticmethod
    def query(ses):
        """Query RPMComparison joined with its packages and their
        repositories.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :return sqlalchemy.orm.query.Query: query
        """
        pkg1 = aliased(RPMPackage, name='pkg1')
        pkg2 = aliased(RPMPackage, name='pkg2')
        repo1 = aliased(RPMRepository, name='repo1')
        repo2 = aliased(RPMRepository, name='repo2')

        return ses.query(
            RPMComparison, Comparison, pkg1, pkg2, repo1, repo2
        ).filter(
            RPMComparison.id_group == Comparison.id,
            RPMComparison.pkg1_id == pkg1.id,
            RPMComparison.pkg2_id == pkg2.id,
            pkg1.id_repo == repo1.id,
            pkg2.id_repo == repo2.id,
        ).order_by(
            RPMComparison.id
        )

    @staticmethod
    def id_from_line(line):
        """Get RPMComparison id from line containing RPMComparison.
        """
        return line.RPMComparison.id

    @staticmethod
    def dict_from_line(line):
        """Get dict from line containing RPMComparison, its packages and their
        repositories."""
        result_dict = line.RPMComparison.exported()
        result_dict['time'] = str(line.Comparison.time)
        result_dict['type'] = constants.COMPARISON_TYPE
        result_dict['pkg1'] = line.pkg1.exported()
        result_dict['pkg2'] = line.pkg2.exported()
        result_dict['pkg1']['filename'] = line.pkg1.rpm_filename()
        result_dict['pkg2']['filename'] = line.pkg2.rpm_filename()
        result_dict['pkg1']['repo'] = line.repo1.exported()
        result_dict['pkg2']['repo'] = line.repo2.exported()
        result_dict['state'] = constants.STATE_STRINGS[result_dict['state']]
        return result_dict

    def comparisons_query(ses, modifiers=None):
        """Query Comparison outer-joined with RPMComparison and its packages
        and their repositories.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param modifiers dict: dict of modifiers and their values
        :return sqlalchemy.orm.query.Query: query
        """
        pkg1 = aliased(RPMPackage, name='pkg1')
        pkg2 = aliased(RPMPackage, name='pkg2')
        repo1 = aliased(RPMRepository, name='repo1')
        repo2 = aliased(RPMRepository, name='repo2')

        query = ses.query(Comparison, ComparisonType).filter(
            ComparisonType.name == constants.COMPARISON_TYPE
        )
        query = modify_query(query, modifiers).from_self()
        query = query.add_entity(RPMComparison).add_entity(pkg1)
        query = query.add_entity(pkg2).add_entity(repo1).add_entity(repo2)
        query = query.outerjoin(
            RPMComparison, RPMComparison.id_group == Comparison.id
        ).filter(
            RPMComparison.id_group == Comparison.id,
            RPMComparison.pkg1_id == pkg1.id,
            RPMComparison.pkg2_id == pkg2.id,
            pkg1.id_repo == repo1.id,
            pkg2.id_repo == repo2.id,
        ).order_by(
            Comparison.id
        )

        return query

    def comparisons_id_from_line(line):
        """Get Comparison id from line containing Comparison.
        """
        return line.Comparison.id

    def comparisons_dict_from_line(line):
        """Get dict from line containing Comparison.
        """
        return {
            'time': str(line.Comparison.time),
            'type': line.ComparisonType.name,
            'state': app_constants.STATE_STRINGS[line.Comparison.state],
        }

class RPMDifference(BaseExported, Base):
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

    @staticmethod
    def query(ses):
        """Query RPMComparison joined with its packages and their repositories,
        outer-joined with RPMDifference.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :return sqlalchemy.orm.query.Query: query
        """
        return RPMComparison.query(ses).add_entity(RPMDifference).outerjoin(
            RPMDifference, RPMDifference.id_comp == RPMComparison.id
        ).order_by(
            RPMComparison.id
        )

    @staticmethod
    def id_from_line(line):
        """Get RPMComparison id from line containing RPMComparison.
        """
        return RPMComparison.line_id(line)

    @staticmethod
    def dict_from_line(line):
        """Get dict from line containing RPMDifference.
        """
        result_dict = line.RPMDifference.exported()
        result_dict['category'] = constants.CATEGORY_STRINGS[
            result_dict['category']
        ]
        result_dict['diff_type'] = constants.DIFF_TYPE_STRINGS[
            result_dict['diff_type']
        ]
        return result_dict

class RPMPackage(BaseExported, Base):
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

    @staticmethod
    def query(ses):
        """Query RPMPackage joined with its repository.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :return sqlalchemy.orm.query.Query: query
        """
        return ses.query(RPMPackage, RPMRepository).filter(
            RPMPackage.id_repo == RPMRepository.id
        ).order_by(RPMPackage.id)

    @staticmethod
    def id_from_line(line):
        """Get RPMPackage id from line containing RPMPackage.
        """
        return line.RPMPackage.id

    @staticmethod
    def dict_from_line(line):
        """Get dict from line containing RPMPackage and its repository.
        """
        result_dict = line.RPMPackage.exported()
        result_dict['filename'] = line.RPMPackage.rpm_filename()
        result_dict['repo'] = line.RPMRepository.exported()
        return result_dict

class RPMRepository(BaseExported, Base):
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

    @staticmethod
    def query(ses):
        """Query RPMRepository.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :return sqlalchemy.orm.query.Query: query
        """
        return ses.query(RPMRepository).order_by(RPMRepository.id)

    @staticmethod
    def id_from_line(line):
        """Get RPMRepository id from line containing only RPMRepository.
        """
        return line.id

    @staticmethod
    def dict_from_line(line):
        """Get dict from line containing only RPMRepository.
        """
        return {'path': line.path}

def general_iter_query_result(result, group_id, group_dict,
                              line_dict=None, name=None):
    """Process query result.

    :param result sqlalchemy.orm.query.Query: query
    :param group_id: function getting id from line of the result
    :param group_dict: function getting dict from line of the result;
        will be called each time id changes
    :param line_dict: function for geting dict from line of the result;
        will be called for every line and agregated into list
    :param name: desired name of the list resulting from the aggregation
    :return: iterator of resulting dict
    :rtype: Iterator[dict]
    """
    last_id = None
    result_dict = None
    outerjoin_items = []

    for line in result:
        if last_id is None:
            # Save new id and dict
            last_id = group_id(line)
            result_dict = group_dict(line)
        if group_id(line) != last_id:
            # Add aggregated list and yield
            if line_dict is not None and result_dict is not None:
                result_dict[name] = outerjoin_items
            yield (last_id, result_dict)
            # Save new id and dict
            last_id = group_id(line)
            result_dict = group_dict(line)
            outerjoin_items = []
        if line_dict is not None:
            item = line_dict(line)
            if item is not None:
                outerjoin_items.append(item)
    # Add aggregated list and yield
    if line_dict is not None and result_dict is not None:
        result_dict[name] = outerjoin_items
    if last_id is not None:
        yield (last_id, result_dict)

def iter_query_result(result, table):
    """Call general_iter_query_result based on given table.

    :param result sqlalchemy.orm.query.Query: query
    :param table: database model

    :return: iterator of resulting dict from general_iter_query_result
    :rtype: Iterator[dict]
    """
    if table == RPMDifference:
        group_id = RPMComparison.id_from_line
        group_dict = RPMComparison.dict_from_line
        line_dict = table.dict_from_line
        name = 'differences'
    elif table == Comparison:
        group_id = RPMComparison.comparisons_id_from_line
        group_dict = RPMComparison.comparisons_dict_from_line
        line_dict = RPMComparison.dict_from_line
        name = 'comparisons'
    else:
        group_id = table.id_from_line
        group_dict = table.dict_from_line
        line_dict = None
        name = None

    return general_iter_query_result(
        result, group_id, group_dict, line_dict=line_dict, name=name
    )
