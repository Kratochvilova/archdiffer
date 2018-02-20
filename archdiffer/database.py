
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
from .constants import STATE_NEW

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
        comparison = Comparison(
            comparison_type_id = comparison_type_id, state=state
        )
        ses.add(comparison)
        ses.commit()
        return comparison

    @staticmethod
    def query(ses):
        """Query Comparison joined with its ComparisonType, ordered by id."""
        return ses.query(Comparison, ComparisonType).filter(
            Comparison.comparison_type_id==ComparisonType.id
        ).order_by(Comparison.id)

class ComparisonType(Base):
    __tablename__ = 'comparison_types'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)

    comparisons = relationship("Comparison", back_populates="comparison_type")

    def __repr__(self):
        return "<ComparisonType(id='%s', name='%s')>" % (self.id, self.name)

    @staticmethod
    def query(ses):
        """Query ComparisonType, ordered by id."""
        return ses.query(ComparisonType).order_by(ComparisonType.id)

class User(Base):
    __tablename__ = 'users'

    openid = Column(String, primary_key=True, nullable=False)
    name = Column(String)
    email = Column(String)

    def __repr__(self):
        return "<User(name='%s')>" % (self.openid)

    @staticmethod
    def query_by_openid(ses, openid):
        """Query User by openid."""
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
        """Get the engine."""
        SessionSingleton.init()
        return SessionSingleton.engine

    @staticmethod
    def get_session(*args, **kwargs):
        """Create new session."""
        return Session(*args, bind=SessionSingleton.get_engine(), **kwargs)

def engine():
    """Get the engine."""
    return SessionSingleton.get_engine()

def session(*args, **kwargs):
    """Get new session."""
    return SessionSingleton.get_session(*args, **kwargs)

def joined_query(ses, table=Comparison):
    """Query database tables jointly.

    :param ses: session for communication with the database
    :type ses: qlalchemy.orm.session.Session
    :param table: table setting which tables to query
    :type table: one of (Comparison, ComparisonType)
    :return sqlalchemy.orm.query.Query: resulting query object
    """
    if table == Comparison:
        return ses.query(Comparison, ComparisonType).filter(
            Comparison.comparison_type_id == ComparisonType.id
        )
    return ses.query(ComparisonType)

def iter_query_result(result, table=Comparison):
    """Process result of the joined query.

    :param result list: query result
    :param table: table setting which tables were queried
    :type table: one of (Comparison, ComparisonType)
    :return: iterator of resulting dict
    :rtype: Iterator[dict]
    """
    def get_id(line):
        """Get id based on table."""
        if table == Comparison:
            return line.Comparison.id
        return line.id

    def parse_line(line):
        """Parse line based on table."""
        result_dict = {}
        if table == Comparison:
            result_dict['time'] = str(line.Comparison.time)
            result_dict['type'] = {
                'id': line.ComparisonType.id,
                'name': line.ComparisonType.name,
            }
        else:
            result_dict = {'name': line.name}

        return result_dict

    for line in result:
        result_id = get_id(line)
        result_dict = parse_line(line)
        yield (result_id, result_dict)
