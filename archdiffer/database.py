# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 19:32:41 2017

@author: pavla
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import config

Base = declarative_base()

class Comparison(Base):
    __tablename__ = 'comparisons'

    id = Column(Integer, primary_key=True, nullable=False)
    # time is set when commited
    time = Column(DateTime, default=func.now())
    module = Column(String, nullable=False)
    pkg1 = Column(String, nullable=False)
    pkg2 = Column(String, nullable=False)
    state = Column(String, nullable=False)
    
    differences = relationship("Difference", back_populates="comparison")

    def __repr__(self):
        return "<Comparison(id='%s', time='%s', module='%s', pkg1='%s', pkg2='%s', state='%s')>" % (
        self.id, self.time, self.module, self.pkg1, self.pkg2, self.state)

    def get_dict(self):
        comparison_dict = {
            'id':self.id,
            'time':self.time,
            'module':self.module,
            'pkg1':self.pkg1,
            'pkg2':self.pkg2,
            'state':self.state
        }
        return comparison_dict

class Difference(Base):
    __tablename__ = 'differences'

    id = Column(Integer, primary_key=True, nullable=False)
    id_comp = Column(Integer, ForeignKey('comparisons.id'), nullable=False)
    pkg =  Column(String, nullable=False)
    diff_type = Column(String, nullable=False)
    diff = Column(String, nullable=False)

    comparison = relationship("Comparison", back_populates="differences")

    def __repr__(self):
        return "<Difference(id='%s', pkg='%s', diff_type='%s', diff='%s')>" % (
        self.id_comp, self.pkg, self.diff_type, self.diff)

    def get_dict(self):
        difference_dict = {
            'id':self.id,
            'id_comp':self.id_comp,
            'pkg':self.pkg,
            'diff_type':self.diff_type,
            'diff':self.diff
        }
        return difference_dict

engine = create_engine(config['common']['DATABASE_URL'], echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
