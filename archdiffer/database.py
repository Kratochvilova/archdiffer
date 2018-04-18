
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 19:32:41 2017

@author: pavla
"""

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import IntegrityError
from .config import config
from .constants import STATE_NEW, STATE_STRINGS

Base = declarative_base()

class Comparison(Base):
    """Database model of comparisons."""
    __tablename__ = 'comparisons'

    id = Column(Integer, primary_key=True, nullable=False)
    # time is set when commited
    time = Column(DateTime, default=func.now())
    comparison_type_id = Column(
        Integer, ForeignKey('comparison_types.id'), nullable=False
    )
    state = Column(Integer, nullable=False, default=STATE_NEW)

    comparison_type = relationship(
        "ComparisonType", back_populates="comparisons"
    )

    def __repr__(self):
        return ("<Comparison(id='%s', time='%s', comparison_type_id='%s', "
                "state='%s')>") % (
                    self.id,
                    datetime.strftime(self.time, '%Y-%m-%d %H:%M:%S'),
                    self.comparison_type_id,
                    self.state,
                )

    def update_state(self, ses, state):
        """Add new Comparison.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param int state: new state
        """
        self.state = state
        ses.add(self)
        ses.commit()

    @staticmethod
    def add(ses, comparison_type_id, state=STATE_NEW):
        """Add new Comparison.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param int comparison_type_id: id of its comparison_type
        :param int state: state
        :return Comparison: newly added Comparison
        """
        comparison = Comparison(
            comparison_type_id=comparison_type_id, state=state
        )
        ses.add(comparison)
        ses.commit()
        return comparison

    @staticmethod
    def query(ses):
        """Query Comparison joined with its ComparisonType.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :return sqlalchemy.orm.query.Query: query
        """
        return ses.query(Comparison, ComparisonType).filter(
            Comparison.comparison_type_id == ComparisonType.id
        ).order_by(Comparison.id)

    @staticmethod
    def id_from_line(line):
        """Get Comparison id from line.

        :param line: named tuple (one item of query result) containing
            Comparison
        :return int: Comparison id
        """
        return line.Comparison.id

    @staticmethod
    def dict_from_line(line):
        """Get dict from line.

        :param line: named tuple (one item of query result) containing
            Comparison and its ComparisonType.
        :return dict: dict with Comparison and ComparisonType column values
        """
        result_dict = {
            'time': datetime.strftime(
                line.Comparison.time, '%Y-%m-%d %H:%M:%S'
            ),
            'state': STATE_STRINGS[line.Comparison.state],
        }
        result_dict['comparison_type'] = {
            'id': line.ComparisonType.id,
            'name': line.ComparisonType.name,
        }
        return result_dict

class ComparisonType(Base):
    """Database model of comparison types."""
    __tablename__ = 'comparison_types'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)

    comparisons = relationship("Comparison", back_populates="comparison_type")

    def __repr__(self):
        return "<ComparisonType(id='%s', name='%s')>" % (self.id, self.name)

    @staticmethod
    def query(ses):
        """Query ComparisonType.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :return sqlalchemy.orm.query.Query: query
        """
        return ses.query(ComparisonType).order_by(ComparisonType.id)

    @staticmethod
    def id_from_line(line):
        """Get ComparisonType id from line.

        :param ComparisonType line: ComparisonType
        :return int: ComparisonType id
        """
        return line.id

    @staticmethod
    def dict_from_line(line):
        """Get dict from line.

        :param ComparisonType line: ComparisonType
        :return dict: dict with ComparisonType column values
        """
        result_dict = {
            'id': line.id,
            'name': line.name,
        }
        return result_dict

class User(Base):
    """Database model of users."""
    __tablename__ = 'users'

    openid = Column(String, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return "<User(openid='%s', name='%s')>" % (
            self.openid, self.name
        )

    @staticmethod
    def query_by_openid(ses, openid):
        """Query User by openid.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param string openid: openid
        :return sqlalchemy.orm.query.Query: query
        """
        return ses.query(User).filter_by(openid=openid).first()

    @staticmethod
    def add(ses, openid, name):
        """Add user to the database if it doesn't already exist.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param string openid: openid
        :param string name: name
        :param string email: email
        :return User: user
        """
        try:
            user = User(openid=openid, name=name)
            ses.add(user)
            ses.commit()
        except IntegrityError:
            ses.rollback()
            user = None
        return user

class SessionSingleton():
    """Singleton that provides sqlalchemy engine and creates sessions."""
    engine = None

    @staticmethod
    def init():
        """Create engine if None."""
        if SessionSingleton.engine is None:
            SessionSingleton.engine = create_engine(
                config['common']['DATABASE_URL'], echo=True
            )

    @staticmethod
    def get_engine():
        """Get the engine.

        :return sqlalchemy.engine.Engine: engine
        """
        SessionSingleton.init()
        return SessionSingleton.engine

    @staticmethod
    def get_session(*args, **kwargs):
        """Create new session.

        :param *args: arguments to be passed when creating session
        :param **kwargs: keyword arguments to be passed when creating session
        :return sqlalchemy.orm.session.Session: session
        """
        return Session(*args, bind=SessionSingleton.get_engine(), **kwargs)

def engine():
    """Get the engine.

    :return sqlalchemy.engine.Engine: engine
    """
    return SessionSingleton.get_engine()

def session(*args, **kwargs):
    """Get new session.

    :param *args: arguments to be passed when creating session
    :param **kwargs: keyword arguments to be passed when creating session
    :return sqlalchemy.orm.session.Session: session
    """
    return SessionSingleton.get_session(*args, **kwargs)

def modify_query(query, modifiers):
    """Modify query according to the modifiers.

    :param sqlalchemy.orm.query.Query query: query to be modified
    :param dict modifiers: dict of modifiers and their values
    :return sqlalchemy.orm.query.Query: modified query
    """
    if modifiers is None:
        return query
    if 'filter_by' in modifiers:
        query = query.filter_by(**modifiers['filter_by'])
    if 'filter' in modifiers:
        query = query.filter(*modifiers['filter'])
    if 'order_by' in modifiers:
        query = query.order_by(*modifiers['order_by'])
    if 'limit' in modifiers:
        query = query.limit(modifiers['limit'])
    if 'offset' in modifiers:
        query = query.offset(modifiers['offset'])
    return query

def general_iter_query_result(result, group_id, group_dict,
                              line_dict=None, name=None):
    """Process query result.

    :param sqlalchemy.orm.query.Query result: query
    :param callable group_id: function getting id from line of the result
    :param callable group_dict: function getting dict from line of the result;
        will be called each time id changes
    :param callable line_dict: function for geting dict from line of the
        result; will be called for every line and agregated into list
    :param string name: desired name of the list resulting from the aggregation
    :return Iterator[dict]: iterator of resulting dict
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

    :param sqlalchemy.orm.query.Query result: query
    :param sqlalchemy.ext.declarative.api.declarativemeta table: database model

    :return: iterator of resulting dict from general_iter_query_result
    :rtype: Iterator[dict]
    """
    group_id = table.id_from_line
    group_dict = table.dict_from_line
    line_dict = None
    name = None

    return general_iter_query_result(
        result, group_id, group_dict, line_dict=line_dict, name=name
    )
