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
    NAME = 'Fahrradfreundliche Schule Bewerbungsformular'
    VERSION = environ.get('DOCKER_IMAGE_VERSION', '')

@final
class directories(ABC):
    STATIC = 'static'
    TEMPLATES = 'templates'

@final
class env(ABC):
    """Names of environmental variables"""
    CONFIG = 'FAHRRADSCHULE_CONFIG_FILE'

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

    FORM_KEY = 'Formular'
    DEFAULT_KEY = 'Vorgabe'
    CITY_KEY = 'Ort'
    ZIPCODE_KEY = 'Postleitzahl'
    QUESTIONS_KEY = 'Fragen'
    LIST_KEY = 'Liste'
    FORM_DEFAULT = {
        DEFAULT_KEY: {
            ZIPCODE_KEY: '',
            CITY_KEY: '',
        },
        QUESTIONS_KEY: {
            LIST_KEY: (
                'coordinator',
                'compass',
                'routemap',
                'parking',
                'repairs',
                'campaign_organizing',
                'campaign_participation',
                'lessons',
            ),
        },
    }

    SECTIONS = (
        (CONTACT_KEY, CONTACT_DEFAULT),
        (FORM_KEY, FORM_DEFAULT),
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

    QUESTIONS_LABELS = {
        'campaign_organizing': 'In der Schule findet pro Jahr mindestens eine Schulaktion zum Thema Fahrrad statt (mind. 2 Klassen machen einen Radausflug, Fahrrad-Reparaturtag, o.ä.).',
        'campaign_participation': 'Die Schule nimmt an einer Fahrrad-Kampagne teil (Stadtradeln, Klimameilen, etc.).',
        'compass': 'Es gibt ein ein Konzept „Mobilitäts-Kompass“, das die Zielsetzung und das Selbstverständnis der Schule als Fahrradfreundliche Schule beinhaltet.',
        'coordinator': 'Es gibt eine Fahrrad-Koordinator*in oder gar eine Fahrrad-AG (mit Lehrer*innen, Schüler*innen und im besten Fall auch Eltern).',
        'lessons': 'Das Thema nachhaltige Mobilität mit dem Fahrrad wird im Unterricht behandelt (Darstellung, wie das Thema in mehreren Klassen behandelt wird).',
        'parking': 'Es gibt ausreichend gute Radabstellanlagen für Schüler*innen und Lehrer*innen.',
        'repairs': 'Es ist eine Fahrrad-Reparaturmöglichkeit vorhanden (Werkzeugkoffer, Reparatursäule o.ä.).',
        'routemap': 'Für ihre Schule gibt es einen aktuellen Schulradwegplan, der die Bedürfnisse der radfahrenden Schülerinnen und Schüler berücksichtigt.',
    }
    CHOICE_YES = 'Ja'
    CHOICE_NO = 'Nein'

    ERROR_INVALID = 'Bitte gib einen gültigen Wert ein.'
    ERROR_LENGTH_ZIPCODE = 'Bitte gib genau '+str(ZIP_DIGITS)+' Ziffern ein.'
    ERROR_REQUIRED = 'Bitte fülle dieses Feld aus.'
    ERROR_REQUIRED_CONSENT = 'Bitte stimme zu.'
    ERROR_REQUIRED_YESNO = 'Bitte wähle '+CHOICE_YES+' oder '+CHOICE_NO+' aus.'
