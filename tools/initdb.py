#!/usr/bin/env python3

from collections.abc import Iterable
import os.path
import pathlib
from sys import stderr

import sqlite3


TEMPLATES_PATH = pathlib.Path(__file__).parent.joinpath('templates')
TEMPLATE_FILE = 'initdb.sql.j2'


def render_sql_commands(**kwargs) -> str:
    import jinja2

    env = jinja2.Environment(loader = jinja2.FileSystemLoader(TEMPLATES_PATH))
    template = env.get_template(TEMPLATE_FILE)
    return template.render(**kwargs)

def create_db(target: str, query: str):
    with sqlite3.connect(target) as conn:
        cursor = conn.cursor()
        cursor.executescript(query)
        conn.commit()


if __name__ == '__main__':
    # Import constants from app
    import argparse
    import pathlib
    import sys

    ROOT = pathlib.Path(__file__).parent.parent.resolve()
    sys.path.append(str(ROOT))

    from app import const

    # Command line parser
    parser = argparse.ArgumentParser(description=f'Creates a new database for use with {const.app.NAME} at DESTINAITON')
    parser.add_argument('target', type=pathlib.Path, metavar='DESTINATION')
    parser.add_argument('-f', '--force', action='store_true', help='overwrite existing files', default=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='count', help='increase verbosity', default=0)
    group.add_argument('-q', '--quiet', action='store_true', help='supress all messages and errors')

    args = parser.parse_args()

    # Check if valid destination
    if args.target.exists():
        if args.force:
            if args.target.is_file():
                args.target.unlink()
                if args.verbose > 0: print('Removed existing file', args.target)
            else:
                if not args.quiet: print(args.target, 'is not a file. Exiting.', file=stderr)
                exit(0 if args.quiet else 3)
        else:
            if not args.quiet: print(args.target, 'already exists. Exiting.', file=stderr)
            exit(0 if args.quiet else 3)

    # Create database
    SQL_QUERY = render_sql_commands(
        tablename=const.form.FORM_NAME,
        questions=const.form.QUESTIONS_LABELS.keys(),
        inputfields=const.form.INPUTFIELDS_LABELS.keys(),
        wholenumfields=const.form.INPUTFIELDS_WHOLENUM,
        fileprefix = const.form.FILE_PREFIX
    )
    if args.verbose > 1:
        print('Parsed template file', str(TEMPLATES_PATH.joinpath(TEMPLATE_FILE)))
    if args.verbose > 2:
        print('\033[0;90m' + SQL_QUERY + '\033[0m')

    create_db(args.target, SQL_QUERY)
    if args.verbose > 0: print('Created', args.target)
