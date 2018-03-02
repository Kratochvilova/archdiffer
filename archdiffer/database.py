
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 19:32:41 2017

@author: pavla
"""

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
        return "<Comparison(id='%s', time='%s', comparison_type_id='%s')>" % (
            self.id, self.time, self.comparison_type_id
        )

    @staticmethod
    def add(ses, comparison_type_id, state=STATE_NEW):
        """Add new Comparison.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param comparison_type_id int: id of its comparison_type
        :param state string: state
        :return Comparison: newly added Comparison
        """
        comparison = Comparison(
            comparison_type_id = comparison_type_id, state=state
        )
        ses.add(comparison)
        ses.commit()
        return comparison

    @staticmethod
    def query(ses, modifiers=None):
        """Query Comparison joined with its ComparisonType.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :return sqlalchemy.orm.query.Query: query
        """
        query = ses.query(Comparison, ComparisonType).filter(
            Comparison.comparison_type_id==ComparisonType.id
        ).order_by(Comparison.id)
        if modifiers is not None:
            query = modify_query(query, modifiers)
        return query

    @staticmethod
    def id_from_line(line):
        """Get Comparison id from line containing Comparison.
        """
        return line.Comparison.id

    @staticmethod
    def dict_from_line(line):
        """Get dict from line containing Comparison and its ComparisonType.
        """
        result_dict = {
            'time': str(line.Comparison.time),
            'state': STATE_STRINGS[line.Comparison.state],
        }
        result_dict['comparison_type'] = {
            'id': line.ComparisonType.id,
            'name': line.ComparisonType.name,
        }
        return result_dict

    @staticmethod
    def count(ses):
        """Count comparisons."""
        return Comparison.query(ses).count()

class ComparisonType(Base):
    __tablename__ = 'comparison_types'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)

    comparisons = relationship("Comparison", back_populates="comparison_type")

    def __repr__(self):
        return "<ComparisonType(id='%s', name='%s')>" % (self.id, self.name)

    @staticmethod
    def query(ses, modifiers=None):
        """Query ComparisonType.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :return sqlalchemy.orm.query.Query: query
        """
        query = ses.query(ComparisonType).order_by(ComparisonType.id)
        if modifiers is not None:
            query = modify_query(query, modifiers)
        return query

    @staticmethod
    def id_from_line(line):
        """Get ComparisonType id from line containing only ComparisonType.
        """
        return line.id

    @staticmethod
    def dict_from_line(line):
        """Get dict from line containing only ComparisonType.
        """
        result_dict = {
            'id': line.id,
            'name': line.name,
        }
        return result_dict

    @staticmethod
    def count(ses):
        """Count comparison_types."""
        return ComparisonType.query(ses).count()

class User(Base):
    __tablename__ = 'users'

    openid = Column(String, primary_key=True, nullable=False)
    name = Column(String)
    email = Column(String)

    def __repr__(self):
        return "<User(name='%s')>" % (self.openid)

    @staticmethod
    def query_by_openid(ses, openid):
        """Query User by openid.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param openid string: openid
        :return sqlalchemy.orm.query.Query: query
        """
        return ses.query(User).filter_by(openid=openid).first()

    @staticmethod
    def add(ses, openid, name, email):
        """Add user to the database if it doesn't already exist.

        :param ses: session for communication with the database
        :type ses: qlalchemy.orm.session.Session
        :param openid string: openid
        :param name string: name
        :param email string: email
        :return: user
        :rtype: database.User
        """
        try:
            user = User(openid=openid, name=name, email=email)
            ses.add(user)
            ses.commit()
        except IntegrityError:
            ses.rollback()
            user = User.query_by_openid(ses, openid)
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
    """
    return SessionSingleton.get_session(*args, **kwargs)


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

def modify_query(query, modifiers):
    """Modify query according to the modifiers.

    :param query sqlalchemy.orm.query.Query: query to be modified
    :param modifiers dict: dict of modifiers and their values
    :return query sqlalchemy.orm.query.Query: modified query
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

def iter_query_result(result, table):
    """Call general_iter_query_result based on given table.

    :param result sqlalchemy.orm.query.Query: query
    :param table: database model

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
