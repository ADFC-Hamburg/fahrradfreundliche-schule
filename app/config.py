"""
Module for parsing a config file.
"""

import tomllib

from . import const


DEFAULT_CONFIG = {key: defaults for key, defaults in const.conf.SECTIONS}


def _deepmerge_without_addition(dst: dict, src: dict) -> dict:
    """
    Replaces values in a destination dictionary
    with values from the source dictionary.
    Subdictionaries are likewise merged rather than replaced.

    This function only replaces values; no new keys are added.
    """
    for key in dst:
        if key not in src:
            continue
        if dst[key] is src[key]:
            continue
        if isinstance(dst[key], dict):
            dst[key] = _deepmerge_without_addition(dst[key], src[key])
        else:
            dst[key] = src[key]
    return dst

def fetch() -> dict:
    """
    Loads and parses the config file,
    substituting default values for missing keys.

    Returns the default config if the config file is unavailable.
    """

    from .paths import CONFIG

    try:
        with open(CONFIG, "rb") as f:
            config = tomllib.load(f)
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        return DEFAULT_CONFIG

    return _deepmerge_without_addition(DEFAULT_CONFIG, config)

def get_contact_details() -> dict:
    return fetch()[const.conf.CONTACT_KEY]

def get_form_config() -> dict:
    return fetch()[const.conf.FORM_KEY]
