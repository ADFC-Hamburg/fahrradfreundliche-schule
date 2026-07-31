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

#region Functions for managing user accounts
def validateuser(username: str, password: str) -> sqlite3.Row | None:
    """Fetches the user account with given username and password
       from the database. Returns None if no matching user exists."""

    query_inserts = {
        'table': const.users.TABLENAME,
        'fields': ', '.join(const.sql.COLUMNS_ALL),
        'filterby': const.users.keys.NAME,
    }
    sql_query = ' '.join((
        const.sql.SELECT,
        const.sql.FILTER
    )) % query_inserts

    with sqlite3.connect(paths.DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql_query, (username,))
        conn.commit()
        row = cursor.fetchone()
    
    if not row:
        return None
    if not row[const.users.keys.SALT] and row[const.users.keys.PASS] == password:
        # Password is stored plain; hash it in the background
        from threading import Thread
        Thread(
            target=setuserpassword,
            kwargs={
                'id': row[const.users.keys.ID],
                'password': row[const.users.keys.PASS],
            },
        ).start()
        return row

    salt = row[const.users.keys.SALT] or ''
    if row[const.users.keys.PASS] == _hash_password(password, salt):
        return row
    return None

def getuserlist(*columns: str) -> list[sqlite3.Row]:
    """Returns a list of user accounts with the specified columns.
       Defaults to all columns."""

    query_inserts = {
        'table': const.users.TABLENAME,
        'fields': ', '.join(columns or const.sql.COLUMNS_ALL),
        'sortfield': const.users.keys.NAME,
    }
    sql_query = ' '.join((
        const.sql.SELECT,
        const.sql.SORT,
    )) % query_inserts

    with sqlite3.connect(paths.DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql_query)
        return cursor.fetchall()

def adduser(**kwargs) -> int:
    """Adds a new user account to the database."""

    salt = _random_salt()
    hashed_password = _hash_password(kwargs.get(const.users.keys.PASS), salt)
    values = {
        const.users.keys.NAME: kwargs.get(const.users.keys.NAME),
        const.users.keys.PASS: hashed_password,
        const.users.keys.SALT: salt,
        **{str(perm): int(kwargs.get(perm)) for perm in const.users.PERMISSIONS},
    }
    query_inserts = {
        'table': const.users.TABLENAME,
        'fields': ', '.join(values.keys()),
        'values': ', '.join(['?'] * len(values))
    }
    sql_query = const.sql.INSERT % query_inserts

    with sqlite3.connect(paths.DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(sql_query, tuple(values.values()))
        new_id = cursor.lastrowid
        conn.commit()
        return new_id

def deleteuser(id: int):
    """Deletes the user account with the given ID. Returns True on
       successful deletion, False if no such application existed."""

    query_inserts = {
        'table': const.users.TABLENAME,
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

def setuserpassword(id: int, password: str):
    """Updates a user account in the database with
       the provided password hashed and salted."""

    salt = _random_salt()
    query_inserts = {
        'table': const.users.TABLENAME,
        'changes': ', '.join((
            f'{const.users.keys.PASS} = "{_hash_password(password, salt)}"',
            f'{const.users.keys.SALT} = "{salt}"',
        )),
        'id': id,
    }
    sql_query = ' '.join((
        const.sql.UPDATE,
        const.sql.FILTER_ID
    )) % query_inserts

    with sqlite3.connect(paths.DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(sql_query)
        conn.commit()
#endregion

#region Helper functions
def _hash_password(password: str, salt: str = '') -> str:
    from hashlib import sha256
    return sha256((password+salt).encode('utf-8')).hexdigest()

def _random_salt() -> str:
    from secrets import token_hex
    return token_hex(32)

def summarize(row: sqlite3.Row) -> str:
    """Returns a formatted text summary of an application."""

    import jinja2

    from . import config

    env = jinja2.Environment(
        loader = jinja2.FileSystemLoader(paths.TEMPLATES),
        extensions=['jinja2.ext.do']
    )
    env.filters['applytimezone'] = config.applytimezone
    template = env.get_template("viewer/summary.txt.j2")
    return template.render(
        row=row,
        questions=const.viewer.CRITERIA_SORTED,
    )
#endregion
