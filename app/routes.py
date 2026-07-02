"""
Module defining URL paths for a flask app
and for rendering content.
"""

# Imports
from flask import Blueprint, jsonify, render_template

from . import config, const, database, uploads, forms, paths

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
        cert = settings[const.conf.CERT_KEY],
        contact = settings[const.conf.CONTACT_KEY],
        custom = settings[const.conf.WEBSITE_KEY],
        uploads = settings[const.conf.FORM_KEY][const.conf.UPLOADS_KEY]
    )

@pages.route('/api/submit', methods=['POST'])
def submit_application():
    webform = forms.ApplicationForm(formconfig=config.get_form_config())
    if webform.validate_on_submit():
        # Put all values into dictionaries
        input_values = {field.short_name: field.data
                        for field in webform.get_inputfields()}
        question_values = {}
        question_filenames = {}
        for key, fields in webform.questions.items():
            question_values[key] = fields[0].data
            if fields[1].data:
                # Save uploaded file; use filename as value
                filename = uploads.add(
                    fields[1].data,
                    webform.school.data,
                    fields[0].short_name,
                )
                question_filenames[const.form.FILE_PREFIX + key] = filename

        # Create database entry
        new_id = database.addapplication(
            **input_values,
            **question_values,
            **question_filenames,
        )

        # Return status message with database entry ID
        return jsonify({
            const.api.STATUS_KEY: const.api.PASS_VALUE,
            const.api.ID_KEY: new_id,
        })

    else:
        # Return status message with validation errors
        return jsonify({
            const.api.STATUS_KEY: const.api.FAIL_VALUE,
            const.api.ERROR_KEY: webform.errors
        })