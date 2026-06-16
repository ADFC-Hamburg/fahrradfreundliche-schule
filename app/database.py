"""Contains functions for interacting with the database."""

import sqlite3

from . import const, paths

def addapplication(**kwargs) -> int:
    """Adds a new application to the database."""

    query_inserts = {
        'table': const.form.FORM_NAME,
        'fields': ', '.join(kwargs.keys()),
        'values': ', '.join(['?'] * len(kwargs))
    }
    sql_query = const.sql.INSERT % query_inserts

    with sqlite3.connect(paths.DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(sql_query, tuple(kwargs.values()))
        new_id = cursor.lastrowid
        conn.commit()
        return new_id
