"""
Provides constants used across this app.
"""

from abc import ABC
from os import environ
from re import compile as compile_regex
from typing import final

@final
class app(ABC):
    """Information about this app."""
    NAME = 'Python Web App Template'
    VERSION = environ.get('DOCKER_IMAGE_VERSION', '')

@final
class directories(ABC):
    STATIC = 'static'
    TEMPLATES = 'templates'

@final
class env(ABC):
    """Names of environmental variables"""
    CONFIG = 'DOCKER_CONFIG_FILE'

@final
class conf(ABC):
    """Keys and default values for the config file."""
    CONTACT_KEY = 'Kontaktdaten'
    URL_KEY = 'Web'
    LEGAL_KEY = 'Impressum'
    PRIVACY_KEY = 'Datenschutz'
    CONTACT_DEFAULT = {
        URL_KEY: {
            LEGAL_KEY: '',
            PRIVACY_KEY: '',
        },
    }

    SECTIONS = (
        (CONTACT_KEY, CONTACT_DEFAULT),
    )

@final
class form(ABC):
    INPUTFIELDS_LABELS = {
        'firstname': 'Vorname',
        'lastname': 'Nachname',
        'email': 'E-Mail-Adresse',
        'school': 'Schule',
        'phone': 'Telefonnummer',
        'address': 'Straße und Hausnummer',
        'zipcode': 'Postleitzahl',
        'city': 'Ort',
        'headcount': 'Anzahl Schülerinnen, Schüler und Lehrkräfte (Gesamt)',
    }
    HEADCOUNT_MAX = 9999
    PHONE_PATTERN = '(\\+\\d)?[ \\d\\-\\/]+\\d'
    PHONE_REGEX = compile_regex('^'+PHONE_PATTERN+'$')
    ZIP_DIGITS = 5
    ZIP_PATTERN = '\\d+'
    ZIP_REGEX = compile_regex('^'+ZIP_PATTERN+'$')
