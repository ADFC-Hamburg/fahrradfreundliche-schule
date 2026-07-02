"""
Provides paths to files and directories.
"""

from os import environ, path

from . import const

ROOT = path.normpath (path.join(path.dirname(__file__), '..'))
STATIC = path.join (ROOT, const.directories.STATIC)
TEMPLATES = path.join (ROOT, const.directories.TEMPLATES)

CONFIG_DEFAULT = path.join (ROOT, 'CONFIG.toml')
CONFIGDIR = environ.get(const.env.CONFIGDIR, ROOT)
CONFIG = environ.get(const.env.CONFIGFILE, path.join(CONFIGDIR, 'CONFIG.toml'))

SAVE_DIR = environ.get(const.env.SAVEDIR, ROOT)
DATABASE = path.join (SAVE_DIR, 'database.db')
UPLOADS = path.join (SAVE_DIR, const.directories.UPLOADS)
