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
    CONFIGDIR = 'FAHRRADSCHULE_CONFIG_DIR'
    CONFIGFILE = 'FAHRRADSCHULE_CONFIG_FILE'

@final
class conf(ABC):
    """Keys and default values for the config file."""
    CONTACT_KEY = 'Kontaktdaten'
    NAME_KEY = 'KreisverbandName'
    PHONE_KEY = 'Telefonnummer'
    MAIL_KEY = 'Email'
    URL_KEY = 'Web'
    HOMEPAGE_KEY = 'Homepage'
    EXAMPLE_KEY = 'BelegeBeispiele'
    LEGAL_KEY = 'Impressum'
    PRIVACY_KEY = 'Datenschutz'
    CONTACT_DEFAULT = {
        NAME_KEY: '',
        PHONE_KEY: '',
        MAIL_KEY: '',
        URL_KEY: {
            HOMEPAGE_KEY: '',
            EXAMPLE_KEY: '',
            LEGAL_KEY: '',
            PRIVACY_KEY: '',
        },
    }

    CERT_KEY = 'Zertifikat'
    VALID_YEARS_KEY = 'GueltigkeitInJahren'
    ENDDATE_KEY = 'EinreichenBisDatum'
    QUALIFICATION_KEY = 'Vorraussetzungen'
    LOCATION_KEY = 'Standort'
    SCHOOLTYPE_KEY = 'Schulformen'
    CERT_DEFAULT = {
        VALID_YEARS_KEY: 0,
        ENDDATE_KEY: '',
        QUALIFICATION_KEY: {
            LOCATION_KEY: '',
            SCHOOLTYPE_KEY: 'Schulen aller Schulformen',
        },
    }

    WEBSITE_KEY = 'Webseite'
    LOGO_KEY = 'Logos'
    APP_KEY = 'FahrradfreundlicheSchule'
    WEBSITE_DEFAULT = {
        LOGO_KEY: {
            APP_KEY: '/static/logos/FFS_generic_logo_small.png',
        },
    }

    FORM_KEY = 'Formular'
    DEFAULT_KEY = 'Vorgabe'
    CITY_KEY = 'Ort'
    ZIPCODE_KEY = 'Postleitzahl'
    QUESTIONS_KEY = 'Fragen'
    LIST_KEY = 'Liste'
    UPLOADS_KEY = 'Belege'
    REQUIRED_KEY = 'Erforderlich'
    FILESIZE_KEY = 'HoechstgroesseInMiB'
    MEDIATYPE_KEY = 'ErlaubteFormate'
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
        UPLOADS_KEY: {
            REQUIRED_KEY: True,
            FILESIZE_KEY: 10,
            MEDIATYPE_KEY: ('image/jpeg', 'image/png', 'application/pdf'),
        }
    }

    SECTIONS = (
        (CONTACT_KEY, CONTACT_DEFAULT),
        (CERT_KEY, CERT_DEFAULT),
        (WEBSITE_KEY, WEBSITE_DEFAULT),
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

    LIST_SEPARATOR = ', '
    LIST_SEPARATOR_LAST = ' oder '

    ERROR_FILESIZE = 'Bitte laden Sie eine Datei hoch, die nicht größer als %i MiB ist.'
    ERROR_INVALID = 'Bitte geben Sie einen gültigen Wert ein.'
    ERROR_LENGTH_ZIPCODE = 'Bitte geben Sie genau '+str(ZIP_DIGITS)+' Ziffern ein.'
    ERROR_MEDIATYPE = 'Bitte laden Sie eine Datei im Format %s hoch.'
    ERROR_REQUIRED = 'Bitte füllen Sie dieses Feld aus.'
    ERROR_REQUIRED_CONSENT = 'Bitte willigen Sie ein.'
    ERROR_REQUIRED_FILE = 'Bitte laden Sie für jedes '+CHOICE_YES+' eine Datei hoch.'
    ERROR_REQUIRED_YESNO = 'Bitte wählen Sie '+CHOICE_YES+' oder '+CHOICE_NO+' aus.'
