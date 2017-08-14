# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 19:32:41 2017

@author: pavla
"""

import time
import sqlite3

class DatabaseConnection(object):

    def __init__(self, database_name):
        # Database connection
        self.con = sqlite3.connect(database_name)
        self.cur = self.con.cursor()

    def get_table(self, table, module=None):
        """Gets all records from a table.
        @param table: table name
        @returns tuple of tuples
        """
        if not table.isalnum():
            return []
        if module is None:
            self.cur.execute('SELECT * FROM %s' % table)
        else:
            self.cur.execute(
                'SELECT * FROM %s WHERE module=?' % table, (module,)
            )
        return self.cur.fetchall()

    def print_all(self):
        """Prints tables comparisons and differences.
        """
        print(self.get_table('comparisons'))
        print(self.get_table('differences'))

    def parse_row_comparisons(self, row):
        """Parses row from comparisons table.
        @param row: tuple with values corresponding to row in table
        @return resulting dict or None if row is invalid
        """
        if len(row) != 6:
            return None

        row_dict = {
            'id': row[0],
            'time': time.strftime("%d %b %Y %H:%M:%S", time.localtime(row[1])),
            'module': row[2],
            'data1': row[3],
            'data2': row[4],
            'state': row[5]
        }
        return row_dict

    def parse_row_differences(self, row):
        """Parses row from differences table.
        @param row: tuple with values corresponding to row in table
        @return resulting dict or None if row is invalid
        """
        if len(row) != 4:
            return None

        row_dict = {
            "id": row[0],
            "data": row[1],
            "diff_type": row[2],
            "diff": row[3]
        }
        return row_dict

    def insert_row_comparisons(self, module, data1, data2, state):
        """Creates record in comparisons table.
        @param db_cur: database connection cursor
        """
        t = time.time()
        self.cur.execute(
            "INSERT INTO comparisons VALUES(?, ?, ?, ?, ?, ?)",
            (None, t, module, data1, data2, state)
        )
        self.con.commit()

    def insert_row_differences(self, id_diff, data, diff_type, diff):
        """Creates record in differences table.
        @param db_cur: database connection cursor
        """
        self.cur.execute(
            "INSERT INTO differences VALUES(?, ?, ?, ?)",
            (id_diff, data, diff_type, diff)
        )
        self.con.commit()

    def get_requests(self, module):
        """Gets all unprocessed records for given module.
        @param module: module name
        @return list of records
        """
        self.cur.execute(
            "SELECT * FROM comparisons WHERE module=? AND state=?",
            (module, 'new',)
        )
        return self.cur.fetchall()

    def set_state(self, id_comp, state):
        """Sets state of record with given id.
        @param id_comp: id
        @param state: state to be set
        """
        self.cur.execute(
            "UPDATE comparisons SET state=? WHERE id=?", (state, id_comp)
        )
        self.con.commit()

    def add_request(self, module, data1, data2):
        """Adds new record into comparisons.
        @param module: module name
        @param data1: name of first archive
        @param data2: name of second archive
        """        
        t = time.time()
        self.cur.execute(
            "INSERT INTO comparisons VALUES(?, ?, ?, ?, ?, ?)",
            (None, t, module, data1, data2, 'new')
        )
        self.con.commit()




from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

Base = declarative_base()

class Comparison(Base):
    __tablename__ = 'comparisons'

    comparison_id = Column(Integer, primary_key=True, nullable=False)
    time = Column(DateTime, default=func.now())
    module = Column(String, nullable=False)
    pkg1 = Column(String, nullable=False)
    pkg2 = Column(String, nullable=False)
    state = Column(String, nullable=False)

    differences = relationship("Difference", back_populates="comparison")
    
    def __init__(self, module, pkg1, pkg2, state):
        # generate id and time
        pass

    def __repr__(self):
        return "<Comparison(id_comparison='%s', time='%s', module='%s', pkg1='%s', pkg2='%s', state='%s')>" % (
        self.comparison_id, self.time, self.module, self.pkg1, self.pkg2, self.state)

class Difference(Base):
    __tablename__ = 'differences'

    comparison_id = Column(Integer, ForeignKey('comparisons.comparison_id'), primary_key=True, nullable=False)
    pkg =  Column(String, primary_key=True, nullable=False)
    diff_type = Column(String, nullable=False)
    diff = Column(String, nullable=False)
    
    comparison = relationship("Comparison", back_populates="differences")

    def __repr__(self):
        return "<Difference(comparison_id='%s', pkg='%s', diff_type='%s', diff='%s')>" % (
        self.comparison_id, self.pkg, self.diff_type, self.diff)


