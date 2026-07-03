"""
Provides constants used across this app.
"""

from abc import ABC
from os import environ
from re import compile as compile_regex
from typing import final

@final
class api(ABC):
    STATUS_KEY = 'status'
    ERROR_KEY = 'errors'
    ID_KEY = 'id'
    PASS_VALUE = 'ok'
    FAIL_VALUE = 'error'

@final
class app(ABC):
    """Information about this app."""
    NAME = 'Fahrradfreundliche Schule Bewerbungsformular'
    VERSION = environ.get('DOCKER_IMAGE_VERSION', '')

@final
class directories(ABC):
    STATIC = 'static'
    TEMPLATES = 'templates'
    UPLOADS = 'documents'

@final
class env(ABC):
    """Names of environmental variables"""
    CONFIGDIR = 'FAHRRADSCHULE_CONFIG_DIR'
    CONFIGFILE = 'FAHRRADSCHULE_CONFIG_FILE'
    SAVEDIR = 'FAHRRADSCHULE_SAVE_DIR'

@final
class conf(ABC):
    """Keys and default values for the config file."""

    @final
    class keys(ABC):
        """Keys used in the config file."""
        APP = 'FahrradfreundlicheSchule'
        CERT = 'Zertifikat'
        CITY = 'Ort'
        CONTACT = 'Kontaktdaten'
        DEFAULT = 'Vorgabe'
        ENDDATE = 'EinreichenBisDatum'
        EXAMPLE = 'BelegeBeispiele'
        FILESIZE = 'HoechstgroesseInMiB'
        FORM = 'Formular'
        HOMEPAGE = 'Homepage'
        LEGAL = 'Impressum'
        LIST = 'Liste'
        LOCATION = 'Standort'
        LOGO = 'Logos'
        MAIL = 'Email'
        MEDIATYPE = 'ErlaubteFormate'
        NAME = 'KreisverbandName'
        PHONE = 'Telefonnummer'
        PRIVACY = 'Datenschutz'
        QUALIFICATION = 'Vorraussetzungen'
        QUESTIONS = 'Fragen'
        REQUIRED = 'Erforderlich'
        SCHOOLTYPE = 'Schulformen'
        SPONSORS = 'Foerderer'
        UPLOADS = 'Belege'
        URL = 'Web'
        VALID_YEARS = 'GueltigkeitInJahren'
        WEBSITE = 'Webseite'
        ZIPCODE = 'Postleitzahl'
        

    CONTACT_DEFAULT = {
        keys.NAME: '',
        keys.PHONE: '',
        keys.MAIL: '',
        keys.URL: {
            keys.HOMEPAGE: '',
            keys.EXAMPLE: '',
            keys.LEGAL: '',
            keys.PRIVACY: '',
        },
    }

    CERT_DEFAULT = {
        keys.VALID_YEARS: 0,
        keys.ENDDATE: '',
        keys.QUALIFICATION: {
            keys.LOCATION: '',
            keys.SCHOOLTYPE: 'Schulen aller Schulformen',
        },
    }

    WEBSITE_DEFAULT = {
        keys.LOGO: {
            keys.APP: '/static/logos/FFS_generic_logo_small.png',
            keys.SPONSORS: (),
        },
    }

    FORM_DEFAULT = {
        keys.DEFAULT: {
            keys.ZIPCODE: '',
            keys.CITY: '',
        },
        keys.QUESTIONS: {
            keys.LIST: (
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
        keys.UPLOADS: {
            keys.REQUIRED: True,
            keys.FILESIZE: 10,
            keys.MEDIATYPE: ('image/jpeg', 'image/png', 'application/pdf'),
        }
    }

    SECTIONS = (
        (keys.CONTACT, CONTACT_DEFAULT),
        (keys.CERT, CERT_DEFAULT),
        (keys.WEBSITE, WEBSITE_DEFAULT),
        (keys.FORM, FORM_DEFAULT),
    )

@final
class form(ABC):
    FORM_NAME = 'applications'

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
    INPUTFIELDS_WHOLENUM = ('headcount',)
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

    FILE_PREFIX = 'filename_'
    FILE_CHAR_REMOVE_PATTERN = '[^A-Za-zÄäÖöÜüß0-9_\\-]'

@final
class sql(ABC):
    INSERT = 'INSERT INTO %(table)s (%(fields)s) VALUES (%(values)s)'
