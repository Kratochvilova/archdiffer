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
    module = Column(String, nullable=False)

    def __repr__(self):
        return "<Comparison(id='%s', module='%s')>" % (self.id, self.module)

class SessionSingleton():
    engine = None

    @staticmethod
    def init():
        if SessionSingleton.engine is None:
            SessionSingleton.engine = create_engine(
                config['common']['DATABASE_URL'], echo=True
            )

    @staticmethod
    def get_engine():
        SessionSingleton.init()
        return SessionSingleton.engine

    @staticmethod
    def get_session(*args, **kwargs):
        return Session(*args, bind=SessionSingleton.get_engine(), **kwargs)

def engine():
    return SessionSingleton.get_engine()

def session(*args, **kwargs):
    return SessionSingleton.get_session(*args, **kwargs)
