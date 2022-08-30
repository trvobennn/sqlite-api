
"""
SQLite 3 database operations

Something like this would be best for backend of an app.
It's not very secure on its own but it has most of the basic database operations.
To make it more secure, segregate read-only operations for users who do not need write access
and have list of existing tables user can choose from to read/write to.
Much easier to keep it secure by referencing a definite set of databases and tables.
Could make the present incarnation more secure by checking function inputs and throwing
them back if found characteristic of injection attacks.

Includes these methods: create table, get table info, commit and roll back changes, insert one and many items,
update and delete items, truncate table, query whole table, query columns, filter query, filter where query,
and close database.

For simplicity, does not have methods built in for linking multiple tables.
"""

import sqlite3
from sqlite3 import Error


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
    except Error as e:
        print(f"The error '{e}' happened.")

    return connection


class Database:
    def __init__(self, db_path, table_name:str):
        self.main_db_ = create_connection(db_path)
        self.cursor = self.main_db_.cursor()
        self.table = table_name

    def create_table(self, table_columns):
        table_string = "CREATE TABLE %s%s;" % (self.table, table_columns)
        self.cursor.execute(table_string)

    def get_table_info(self):
        self.cursor.execute('SELECT * FROM sqlite_master;')
        return self.cursor.fetchall()

    def tidy_print(self):
        for item in self.query_whole_table():
            print(item)

    def commit_change(self):
        self.main_db_.commit()

    def rollback_change(self):
        self.main_db_.rollback()

    def insert_one(self, data_tuple:tuple):
        # for autoincrementing value, use None placeholder
        placeholder = '?' + (',?'*(len(data_tuple)-1))
        insert_str = "INSERT INTO %s VALUES(%s)" % (self.table, placeholder)
        self.cursor.execute(insert_str, data_tuple)

    def insert_many(self, data_list:list):
        for insert_item in data_list:
            self.insert_one(insert_item)

    def update_item(self, col_id, col_info, index, row_id):
        # give table name, then column name, then new info to insert,
        # the label to index by, and the id for the index
        upd_str = "UPDATE %s SET %s = ? WHERE %s = ?" % (self.table, col_id, index)
        self.cursor.execute(upd_str, (col_info, row_id))

    def delete_item(self, column, row_id):
        delet_str = "DELETE FROM %s WHERE %s = ?" % (self.table, column)
        self.cursor.execute(delet_str, (row_id,))

    def truncate_table(self):
        trunc_str = "TRUNCATE TABLE %s" % self.table
        self.cursor.execute(trunc_str)

    def query_whole_table(self):
        query_str = "SELECT * from %s" % self.table
        self.cursor.execute(query_str)
        return self.cursor.fetchall()

    def query_col_in_table(self, column_name:str):
        query_str = "SELECT %s from %s" % (column_name,self.table)
        self.cursor.execute(query_str)
        return self.cursor.fetchall()

    def col_filter_query(self, filter_by, columns, desc=True):
        query_str = ""
        column_str = ''
        for ind, item in enumerate(columns):
            column_str += item
            if ind < len(columns)-1:
                column_str += ', '
        if desc:
            query_str = "SELECT %s FROM %s ORDER BY %s DESC" % (column_str, self.table, filter_by)
        elif not desc:
            query_str = "SELECT %s FROM %s ORDER BY %s ASC" % (column_str, self.table, filter_by)

        self.cursor.execute(query_str)
        return self.cursor.fetchall()

    def filter_fine_query(self, where_col, target, columns, sign='=', asc=True):
        # sign can be any normal comparison sign: <,>,=,<=,>=,!=
        columns_f = ''
        for ind, item in enumerate(columns):
            columns_f += item
            if ind < len(columns)-1:
                columns_f += ', '
        filter_str = f"SELECT {columns_f} FROM {self.table} WHERE %s %s ? ORDER BY {where_col}" % (where_col,sign)
        if asc:
            self.cursor.execute(filter_str, (target,))
        if not asc:
            filter_str += f" DESC"
            self.cursor.execute(filter_str, (target,))
        return self.cursor.fetchall()

    def filter_where_query(self, where_col, target, sign='='):
        # sign can be any normal comparison sign: <,>,=,<=,>=,!=
        filter_str = f"SELECT * FROM {self.table} WHERE %s %s ?;" % (where_col,sign)
        self.cursor.execute(filter_str,(target,))
        return self.cursor.fetchall()

    def close(self):
        self.main_db_.close()
