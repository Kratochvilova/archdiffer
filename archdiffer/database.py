# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 19:32:41 2017

@author: pavla
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session
from .config import config

Base = declarative_base()

class Comparison(Base):
    __tablename__ = 'comparisons'

    id = Column(Integer, primary_key=True, nullable=False)
    plugin = Column(String, nullable=False)

    def __repr__(self):
        return "<Comparison(id='%s', plugin='%s')>" % (self.id, self.plugin)

    def get_dict(self):
        comparison_dict = {
            'id':self.id,
            'plugin':self.plugin
        }
        return comparison_dict

class Plugin(Base):
    __tablename__ = 'plugins'

    id = Column(Integer, primary_key=True, nullable=False)
    plugin = Column(String, nullable=False)

    def __repr__(self):
        return "<Plugin(id='%s', plugin='%s')>" % (self.id, self.plugin)

    def get_dict(self):
        plugin_dict = {
            'id':self.id,
            'plugin':self.plugin
        }
        return plugin_dict

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
