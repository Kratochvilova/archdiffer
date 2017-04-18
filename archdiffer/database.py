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

    def get_table(self, table):
        """Gets all records from a table.
        @param table: table name
        @returns tuple of tuples
        """
        self.cur.execute('SELECT * FROM %s' % table)
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
            'time': row[1],
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
