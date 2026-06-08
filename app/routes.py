"""
Module defining URL paths for a flask app
and for rendering content.
"""

# Imports
from flask import Blueprint, render_template

from . import config, const, paths

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
    'conf': const.conf,
    'contact': config.get_contact_details(),
}

@pages.route('/index')
@pages.route('/')
def index():
    return render_template('index.html.j2', **_CONTEXT)
