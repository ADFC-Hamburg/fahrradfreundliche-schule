"""Contains functions for interacting with the database."""

from collections.abc import Iterable
import sqlite3

from . import const, paths

#region Functions for managing applications
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

def getapplication(id: int, *columns: str) -> sqlite3.Row | None:
    """Returns the specified columns of the application with the
       specified ID. Defaults to all columns."""

    query_inserts = {
        'table': const.form.FORM_NAME,
        'fields': ', '.join(columns or const.sql.COLUMNS_ALL),
        'id': id,
    }
    sql_query = ' '.join((
        const.sql.SELECT,
        const.sql.FILTER_ID,
    )) % query_inserts

    with sqlite3.connect(paths.DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql_query)
        return cursor.fetchone()

def getapplicationlist(*columns: str) -> list[sqlite3.Row]:
    """Returns a list of applications with the specified columns.
       Defaults to all columns."""

    query_inserts = {
        'table': const.form.FORM_NAME,
        'fields': ', '.join(columns or const.sql.COLUMNS_ALL),
        'sortfield': 'id',
    }
    sql_query = ' '.join((
        const.sql.SELECT,
        const.sql.SORT_DESC,
    )) % query_inserts

    with sqlite3.connect(paths.DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql_query)
        return cursor.fetchall()

def deleteapplication(id: int) -> bool:
    """Deletes the application with the given ID. Returns True on
       successful deletion, False if no such application existed."""

    query_inserts = {
        'table': const.form.FORM_NAME,
        'id': id,
    }
    sql_query = ' '.join((
        const.sql.DELETE,
        const.sql.FILTER_ID,
    )) % query_inserts

    with sqlite3.connect(paths.DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(sql_query)
        conn.commit()
        return bool(cursor.rowcount)
#endregion

#region Functions for querying filename columns
def getfilenames(id: int) -> dict[str, str]:
    """Returns a dictionary containing the names of all files
       belonging to an application with the provided ID."""

    row = getapplication(id, *const.sql.COLUMNS_FILES)
    if not row: return {}

    result = {}
    for key in row.keys():
        if row[key]:
            result[key] = row[key]
    return result

def filterdanglingfiles(*filenames: str) -> list[str]:
    """Checks which of the given filenames are still referenced in the
       database and returns a list of only unreferenced filenames."""

    if not filenames: return []

    dangling_files = list()
    query_inserts = {
        'table': const.form.FORM_NAME,
        'fields': '1',
    }
    sql_query = const.sql.EXISTS % ' '.join((
        const.sql.SELECT % query_inserts,
        const.sql.ANY_FILE
    ))
    with sqlite3.connect(paths.DATABASE) as conn:
        cursor = conn.cursor()
        for filename in filenames:
            cursor.execute(sql_query % {'value': filename})
            if not cursor.fetchone()[0]:
                dangling_files.append(filename)
    return dangling_files
#endregion
