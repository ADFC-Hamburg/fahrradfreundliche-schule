"""
Module for parsing a config file.
"""

import tomllib

from . import const

def fetch() -> configparser.ConfigParser:
    from .paths import CONFIG

    with open(CONFIG, "rb") as f:
        config = tomllib.load(f)
    return config

def get_contact_details() -> dict:
    try:
        contacts = fetch()[const.conf.CONTACT_KEY]
        return const.conf.CONTACT_DEFAULT | contacts
    except FileNotFoundError:
        return const.conf.CONTACT_DEFAULT
