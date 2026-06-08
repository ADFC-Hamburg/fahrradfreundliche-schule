"""
Provides constants used across this app.
"""

from abc import ABC
from os import environ
from typing import final

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
    CONTACT_KEY = 'contact'
    URL_KEY = 'url'
    LEGAL_KEY = 'legal'
    PRIVACY_KEY = 'privacy'
    CONTACT_DEFAULT = {
        URL_KEY: {
            LEGAL_KEY: '',
            PRIVACY_KEY: '',
        },
    }
