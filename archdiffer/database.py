
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
from .config import config

Base = declarative_base()

class Comparison(Base):
    __tablename__ = 'comparisons'

    id = Column(Integer, primary_key=True, nullable=False)
    # time is set when commited
    time = Column(DateTime, default=func.now())
    comparison_type_id = Column(
        Integer, ForeignKey('comparison_types.id'), nullable=False
    )

    comparison_type = relationship(
        "ComparisonType", back_populates="comparisons"
    )

    def __repr__(self):
        return "<Comparison(id='%s', time='%s', comparison_type_id='%s')>" % (
            self.id, self.time, self.comparison_type_id
        )

class ComparisonType(Base):
    __tablename__ = 'comparison_types'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)

    comparisons = relationship("Comparison", back_populates="comparison_type")

    def __repr__(self):
        return "<ComparisonType(id='%s', name='%s')>" % (self.id, self.name)

class User(Base):
    __tablename__ = 'users'

    openid = Column(String, primary_key=True, nullable=False)
    name = Column(String)
    email = Column(String)

    def __repr__(self):
        return "<User(name='%s')>" % (self.openid)

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
