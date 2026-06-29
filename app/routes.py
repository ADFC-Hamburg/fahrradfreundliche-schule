"""
Module defining URL paths for a flask app
and for rendering content.
"""

# Imports
from flask import Blueprint, render_template

from . import config, const, forms, paths

# Constants
_BLUEPRINT_NAME = 'pages'
_STATIC_ENDPOINT = _BLUEPRINT_NAME + '.static'

# Routes
pages = Blueprint(_BLUEPRINT_NAME, __name__,
                  template_folder=paths.TEMPLATES,
                  static_folder=paths.STATIC,
                  static_url_path='/static')

_CONTEXT = {
    # Values to be passed to all templates
    'static': _STATIC_ENDPOINT,
    'appname': const.app.NAME,
    'conf': const.conf,
    'version': const.app.VERSION
}

@pages.route('/index', methods=['GET','POST'])
@pages.route('/', methods=['GET','POST'])
def index():
    settings = config.fetch()
    webform = forms.ApplicationForm(
        formconfig=settings[const.conf.FORM_KEY],
    )
    return render_template(
        'index.html.j2', **_CONTEXT,
        form = webform,
        contact = settings[const.conf.CONTACT_KEY],
    )
