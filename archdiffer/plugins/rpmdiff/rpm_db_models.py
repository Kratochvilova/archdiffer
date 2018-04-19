# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 10:56:53 2017

@author: pavla
"""

from datetime import datetime
from sqlalchemy import (Column, Integer, String, Text, Boolean, DateTime,
                        ForeignKey, func)
from sqlalchemy.orm import relationship, backref, aliased
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.exc import IntegrityError
from ... database import (Base, Comparison, ComparisonType, User,
                          general_iter_query_result)
from . import constants
from ... import constants as app_constants

class BaseExported(object):
    """For exporting attributes from the models."""
    to_export = []

    def exported(self, overwrite=None):
        """Export attributes.

        :param list overwrite: list of attribute strings to be exported instead
            of the default ones
        :return dict: {attribute string: attribute value}
        """
        if overwrite is None:
            overwrite = self.to_export
        return {k:v for k, v in vars(self).items() if k in overwrite}

class RPMComparison(BaseExported, Base):
    """Database model of rpm comparisons."""
    __tablename__ = 'rpm_comparisons'

    to_export = ['id', 'state']

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

    comparison = relationship("Comparison", backref=backref("rpm_comparison"))

    rpm_comments = relationship("RPMComment", back_populates="rpm_comparison")

    def __repr__(self):
        return ("<RPMComparison(id='%s', id_group='%s', pkg1_id='%s', "
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
        :param int state: new state
        """
        self.state = state
        ses.add(self)
        ses.commit()

    def update_group_state(self, ses, state):
        """Update state of the Comparison.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param int state: new state
        """
        self.comparison.update_state(ses, state)

    @staticmethod
    def add(ses, rpm_package1, rpm_package2, id_group=None):
        """Add new RPMComparison together with corresponding Comparison.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param RPMPackage rpm_package1: first package
        :param RPMPackage rpm_package2: second package
        :return RPMComparison: newly added RPMComparison
        """
        if id_group is None:
            comparison_type_id = ses.query(ComparisonType).filter_by(
                name=constants.COMPARISON_TYPE
            ).one().id
            comparison = Comparison.add(ses, comparison_type_id)
            id_group = comparison.id

        rpm_comparison = RPMComparison(
            id_group=id_group,
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
        query = ses.query(
            RPMComparison, Comparison, pkg1, pkg2, repo1, repo2
        ).filter(
            RPMComparison.id_group == Comparison.id,
            RPMComparison.pkg1_id == pkg1.id,
            RPMComparison.pkg2_id == pkg2.id,
            pkg1.id_repo == repo1.id,
            pkg2.id_repo == repo2.id,
        )
        return query

    @staticmethod
    def id_from_line(line):
        """Get RPMComparison id from line.

        :param line: named tuple (one item of query result) containing
            RPMComparison
        :return int: RPMComparison id
        """
        return line.RPMComparison.id

    @staticmethod
    def dict_from_line(line):
        """Get dict from line.

        :param line: named tuple (one item of query result) containing
            RPMComparison its packages and their repositories.
        :return dict: dict with RPMComparison, packages and repositories
            column values
        """
        result_dict = None
        if line.RPMComparison is not None:
            result_dict = {
                'id': line.RPMComparison.id,
                'id_group': line.RPMComparison.id_group,
                'state': constants.STATE_STRINGS[line.RPMComparison.state],
                'time': datetime.strftime(
                    line.Comparison.time, '%Y-%m-%d %H:%M:%S'
                ),
                'type': constants.COMPARISON_TYPE,
                'pkg1': line.pkg1.exported(),
                'pkg2': line.pkg2.exported(),
            }
            result_dict['pkg1']['filename'] = line.pkg1.rpm_filename()
            result_dict['pkg2']['filename'] = line.pkg2.rpm_filename()
            result_dict['pkg1']['repo'] = line.repo1.exported()
            result_dict['pkg2']['repo'] = line.repo2.exported()
        return result_dict

    @staticmethod
    def query_group_ids(ses):
        """Query Comparison.id outer-joined with RPMComparison and its packages
        and their repositories.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :return sqlalchemy.orm.query.Query: query
        """
        query = ses.query(Comparison.id).join(ComparisonType).filter(
            ComparisonType.name == constants.COMPARISON_TYPE
        ).outerjoin(
            RPMComparison, RPMComparison.id_group == Comparison.id
        ).outerjoin(
            pkg1, RPMComparison.pkg1_id == pkg1.id
        ).outerjoin(
            pkg2, RPMComparison.pkg2_id == pkg2.id
        ).outerjoin(
            repo1, pkg1.id_repo == repo1.id,
        ).outerjoin(
            repo2, pkg2.id_repo == repo2.id,
        )
        return query

    @staticmethod
    def query_groups(ses, group_ids):
        """Query Comparison joined with query of Comparison.id, outer-joined
        with RPMComparison and its packages and their repositories.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param sqlalchemy.orm.query.Query group_ids: query of Comparison.id
        :return sqlalchemy.orm.query.Query: query
        """
        query = ses.query(Comparison).join(
            group_ids, group_ids.c.id == Comparison.id
        )
        query = query.add_entity(ComparisonType).filter(
            ComparisonType.name == constants.COMPARISON_TYPE
        )
        query = query.add_entity(RPMComparison).outerjoin(
            RPMComparison, RPMComparison.id_group == Comparison.id
        )
        query = query.add_entity(pkg1).outerjoin(
            pkg1, RPMComparison.pkg1_id == pkg1.id
        )
        query = query.add_entity(pkg2).outerjoin(
            pkg2, RPMComparison.pkg2_id == pkg2.id
        )
        query = query.add_entity(repo1).outerjoin(
            repo1, pkg1.id_repo == repo1.id
        )
        query = query.add_entity(repo2).outerjoin(
            repo2, pkg2.id_repo == repo2.id
        )
        return query

    @staticmethod
    def id_from_line_groups(line):
        """Get Comparison id from line.

        :param line: named tuple (one item of query result) containing
            Comparison
        :return int: Comparison id
        """
        return line.Comparison.id

    @staticmethod
    def dict_from_line_groups(line):
        """Get dict from line.

        :param line: named tuple (one item of query result) containing
            Comparison.
        :return dict: dict with Comparison column values
        """
        return {
            'time': datetime.strftime(
                line.Comparison.time, '%Y-%m-%d %H:%M:%S'
            ),
            'type': line.ComparisonType.name,
            'state': app_constants.STATE_STRINGS[line.Comparison.state],
        }

class RPMDifference(BaseExported, Base):
    """Database model of rpm differences."""
    __tablename__ = 'rpm_differences'

    to_export = [
        'id', 'category', 'diff_type', 'diff_info', 'diff', 'state', 'waived'
    ]

    id = Column(Integer, primary_key=True, nullable=False)
    id_comp = Column(
        Integer, ForeignKey('rpm_comparisons.id'), nullable=False
    )
    category = Column(Integer)
    diff_type = Column(Integer, nullable=False)
    diff_info = Column(String(255))
    diff = Column(String(255), nullable=False)
    state = Column(Integer, nullable=False)
    waived = Column(Boolean, nullable=False)

    rpm_comparison = relationship(
        "RPMComparison", back_populates="rpm_differences"
    )

    rpm_comments = relationship("RPMComment", back_populates="rpm_difference")

    def __repr__(self):
        return ("<RPMDifference(id='%s', id_comp='%s', category='%s', "
                "diff_type='%s', diff_info='%s', diff='%s', state='%s')>") % (
                    self.id,
                    self.id_comp,
                    self.category,
                    self.diff_type,
                    self.diff_info,
                    self.diff,
                    self.state,
                )

    def update_state(self, ses, state):
        """Update state of the RPMDifference.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param int state: new state
        """
        self.state = state
        ses.add(self)
        ses.commit()

    def waive(self, ses):
        """Set/clear waive flag.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        """
        if self.waived:
            self.waived = False
        else:
            self.waived = True
        ses.add(self)
        ses.commit()

    @staticmethod
    def add(ses, id_comp, category, diff_type, diff_info, diff,
            state=constants.DIFF_STATE_NORMAL):
        """Add new RPMDifference.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param int id_comp: id of corresponding comparison
        :param int category: category
        :param int diff_type: diff type
        :param string diff_info: diff_info
        :param string diff: diff
        :param int state: state
        :return RPMDifference: newly added RPMDifference
        """
        difference = RPMDifference(
            id_comp=id_comp,
            category=category,
            diff_type=diff_type,
            diff_info=diff_info,
            diff=diff,
            state=state,
            waived=False,
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
        query = RPMComparison.query(ses)
        query = query.add_entity(RPMDifference).outerjoin(
            RPMDifference, RPMDifference.id_comp == RPMComparison.id
        )
        return query

    @staticmethod
    def id_from_line(line):
        """Get RPMComparison id from line containing RPMComparison.

        :param line: named tuple (one item of query result) containing
            RPMComparison
        :return int: RPMComparison id
        """
        return RPMComparison.line_id(line)

    @staticmethod
    def dict_from_line(line):
        """Get dict from line.

        :param line: named tuple (one item of query result) containing
            RPMDifference.
        :return dict: dict with RPMDifference column values
        """
        result_dict = None
        if line.RPMDifference is not None:
            result_dict = line.RPMDifference.exported()
            result_dict['category'] = constants.CATEGORY_STRINGS[
                result_dict['category']
            ]
            result_dict['diff_type'] = constants.DIFF_TYPE_STRINGS[
                result_dict['diff_type']
            ]
            result_dict['state'] = constants.DIFF_STATE_STRINGS[
                result_dict['state']
            ]
        return result_dict

class RPMPackage(BaseExported, Base):
    """Database model of rpm packages."""
    __tablename__ = 'rpm_packages'

    to_export = ['id', 'name', 'arch', 'epoch', 'version', 'release']

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    arch = Column(String(255), nullable=False)
    epoch = Column(String(255), nullable=False)
    version = Column(String(255), nullable=False)
    release = Column(String(255), nullable=False)
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
        return ("<RPMPackage(id='%s', name='%s', arch='%s', epoch='%s', "
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

        :param dnf.package.Package package: corresponds to an RPM file
        :return string: RPM filename
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
        :param dnf.package.Package package: corresponds to an RPM file
        :param string repo_path: repository baseurl
        :return rpm_db_models.RPMPackage: package
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
        query = ses.query(RPMPackage, RPMRepository).filter(
            RPMPackage.id_repo == RPMRepository.id
        )
        return query

    @staticmethod
    def id_from_line(line):
        """Get RPMPackage id from line.

        :param line: named tuple (one item of query result) containing
            RPMPackage
        :return int: RPMPackage id
        """
        return line.RPMPackage.id

    @staticmethod
    def dict_from_line(line):
        """Get dict from line.

        :param line: named tuple (one item of query result) containing
            RPMPackage and its RPMRepository
        :return dict: dict of RPMPackage and RPMRepository column values
        """
        result_dict = line.RPMPackage.exported()
        result_dict['filename'] = line.RPMPackage.rpm_filename()
        result_dict['repo'] = line.RPMRepository.exported()
        return result_dict

class RPMRepository(BaseExported, Base):
    """Database model of rpm repositories."""
    __tablename__ = 'rpm_repositories'

    to_export = ['id', 'path']

    id = Column(Integer, primary_key=True, nullable=False)
    path = Column(String(255), nullable=False, unique=True)

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
        :param string repo_path: repository baseurl
        :return rpm_db_models.RPMRepository: repository
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
        query = ses.query(RPMRepository)
        return query

    @staticmethod
    def id_from_line(line):
        """Get RPMRepository id from line.

        :param RPMRepository line: RPMRepository
        :return int: RPMRepository id
        """
        return line.id

    @staticmethod
    def dict_from_line(line):
        """Get dict from line.

        :param RPMRepository line: RPMRepository
        :return dict: dict of RPMRepository column values
        """
        return {'path': line.path}

class RPMComment(BaseExported, Base):
    """Database model of rpm comments."""
    __tablename__ = 'rpm_comments'

    to_export = ['id', 'text']

    id = Column(Integer, primary_key=True, nullable=False)
    # time is set when commited
    time = Column(DateTime, default=func.now())
    text = Column(Text)
    id_user = Column(String(255), ForeignKey('users.openid'), nullable=False)
    id_comp = Column(Integer, ForeignKey('rpm_comparisons.id'))
    id_diff = Column(Integer, ForeignKey('rpm_differences.id'))

    user = relationship("User", backref=backref("rpm_comments"))
    rpm_comparison = relationship(
        "RPMComparison", back_populates="rpm_comments"
    )
    rpm_difference = relationship(
        "RPMDifference", back_populates="rpm_comments"
    )

    def __repr__(self):
        return ("<Comment(id='%s', time='%s', text='%s', id_user='%s', "
                "id_comp='%s', id_diff='%s')>") % (
                    self.id,
                    datetime.strftime(self.time, '%Y-%m-%d %H:%M:%S'),
                    self.text,
                    self.id_user,
                    self.id_comp,
                    self.id_diff
                )

    @staticmethod
    def add(ses, text, id_user, id_comp=None, id_diff=None):
        """Add comment to the database.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param string text: text of the comment
        :param string id_user: openid of the author
        :param int id_comp: id of related rpm comparison
        :param int id_diff: id of related rpm difference
        :return Comment: comment
        """
        comment = RPMComment(
            text=text,
            id_user=id_user,
            id_comp=id_comp,
            id_diff=id_diff
        )
        ses.add(comment)
        ses.commit()
        return comment

    @staticmethod
    def query(ses):
        """Query RPMComment.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :return sqlalchemy.orm.query.Query: query
        """
        query = ses.query(RPMComment, User).filter(
            RPMComment.id_user == User.openid
        ).add_entity(RPMComparison).outerjoin(
            RPMComparison, RPMComparison.id == RPMComment.id_comp
        ).add_entity(RPMDifference).outerjoin(
            RPMDifference, RPMDifference.id == RPMComment.id_diff
        )
        return query

    @staticmethod
    def id_from_line(line):
        """Get RPMComment id from line.

        :param RPMComment line: RPMComment
        :return int: RPMComment id
        """
        return line.RPMComment.id

    @staticmethod
    def dict_from_line(line):
        """Get dict from line.

        :param RPMComment line: RPMComment
        :return dict: dict of RPMComment column values
        """
        result_dict = line.RPMComment.exported()
        result_dict['time'] = datetime.strftime(
            line.RPMComment.time, '%Y-%m-%d %H:%M:%S'
        )
        result_dict['username'] = line.User.name
        if line.RPMComparison is not None:
            result_dict['comparison'] = line.RPMComparison.exported()
        if line.RPMDifference is not None:
            result_dict['difference'] = line.RPMDifference.exported()
        return result_dict

def iter_query_result(result, table):
    """Call general_iter_query_result based on given table.

    :param sqlalchemy.orm.query.Query result: query
    :param sqlalchemy.ext.declarative.api.declarativemeta table: database model

    :return: iterator of resulting dict from general_iter_query_result
    :rtype: Iterator[dict]
    """
    if table == RPMDifference:
        group_id = RPMComparison.id_from_line
        group_dict = RPMComparison.dict_from_line
        line_dict = table.dict_from_line
        name = 'differences'
    elif table == Comparison:
        group_id = RPMComparison.id_from_line_groups
        group_dict = RPMComparison.dict_from_line_groups
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

pkg1 = aliased(RPMPackage, name='pkg1')
pkg2 = aliased(RPMPackage, name='pkg2')
repo1 = aliased(RPMRepository, name='repo1')
repo2 = aliased(RPMRepository, name='repo2')
