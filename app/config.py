"""
Module for parsing a config file.
"""

import tomllib

from . import const


DEFAULT_CONFIG = {key: defaults for key, defaults in const.conf.SECTIONS}

cached_config = DEFAULT_CONFIG
cache_timestamp = None


def _deepmerge_without_addition(dst: dict, src: dict) -> dict:
    """
    Replaces values in a destination dictionary
    with values from the source dictionary.
    Subdictionaries are likewise merged rather than replaced.

    This function only replaces values; no new keys are added.
    """
    out = {}
    for key in dst:
        if key not in src or dst[key] is src[key]:
            out[key] = dst[key]
        elif isinstance(dst[key], dict):
            out[key] = _deepmerge_without_addition(dst[key], src[key])
        else:
            out[key] = src[key]
    return out

def fetch() -> dict:
    """
    Loads and parses the config file,
    substituting default values for missing keys.

    Returns the default config if the config file is unavailable.
    """

    from os.path import getmtime

    from .paths import CONFIG

    global cached_config, cache_timestamp

    try:
        file_timestamp = getmtime(CONFIG)
        if file_timestamp == cache_timestamp:
            # Return cache if cache is up to date
            return cached_config

        with open(CONFIG, "rb") as f:
            config = tomllib.load(f)
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        return DEFAULT_CONFIG

    # Substitute missing values with defaults; cache the result
    cached_config = _deepmerge_without_addition(DEFAULT_CONFIG, config)
    cache_timestamp = file_timestamp

    return cached_config
