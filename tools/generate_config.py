#!/usr/bin/env python3

"""
Module for formatting settings in TOML format.
If run as an executable, writes a default config to STDOUT.
"""

from collections.abc import Iterable
import os.path


def render_config_template(appname: str, sections: Iterable[Iterable[str, dict], ...]) -> str:
    """
    Takes the app name and a list of sections (name and settings as dict);
    Returns a TOML configuration file with those sections.
    """
    import jinja2

    templates_path = os.path.join(os.path.dirname(__file__), 'templates')
    env = jinja2.Environment(loader = jinja2.FileSystemLoader(templates_path))
    template = env.get_template("config.toml.j2")
    formatted = tuple((header, format_settings(extract_nested_keys(content)))
                               for header, content in sections)
    return template.render(appname=appname,sections=formatted)

def format_settings(settings: tuple[tuple[tuple[str, ...], any], ...]) -> tuple[tuple[str, str], ...]:
    """
    For each setting in tuple: replace list of keys with period-separated
    string; escape special characters; turn numbers into strings.
    """
    output = list()
    for key, value in settings:
        key = '.'.join(key)
        if isinstance(value,(int,float)):
            value = str(value)
        else:
            value = '"' + str(value).replace('\\','\\\\').replace('"','\\"') + '"'
        output.append((key, value))
    return tuple(output)

def extract_nested_keys(dictionary: dict) -> tuple[tuple[tuple[str, ...], any], ...]:
    """
    Parses a dict of settings and returns them as tuples containing
    key(s) and value; Dictionaries within dictionaries are flattened out.
    """
    output = list()
    for key, value in dictionary.items():
        if isinstance(value, dict):
            for subkey, subvalue in extract_nested_keys(value):
                output.append(((key, *subkey), subvalue))
        else:
            output.append(((key,), value))
    return tuple(output)


if __name__ == '__main__':
    # Import constants from app
    import sys

    ROOT = (os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(ROOT)

    from app import const

    # Render and print default config to STDOUT
    print (render_config_template(const.app.NAME, const.conf.SECTIONS))
