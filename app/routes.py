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
    'keys': const.conf.keys,
    'version': const.app.VERSION
}

@pages.route('/index')
@pages.route('/')
def index():
    settings = config.fetch()
    webform = forms.ApplicationForm(
        formconfig=settings[const.conf.keys.FORM],
    )
    return render_template(
        'index.html.j2', **_CONTEXT,
        form = webform,
        cert = settings[const.conf.keys.CERT],
        contact = settings[const.conf.keys.CONTACT],
        custom = settings[const.conf.keys.WEBSITE],
        uploads = settings[const.conf.keys.FORM][const.conf.keys.UPLOADS]
    )

@pages.route('/api/submit', methods=['POST'])
def submit_application():
    settings = config.fetch()
    webform = forms.ApplicationForm(formconfig=settings[const.conf.keys.FORM])
    if webform.validate_on_submit():
        # Put all values into dictionaries
        input_values = {field.short_name: field.data
                        for field in webform.get_inputfields()}
        question_values = {}
        question_filenames = {}
        for key, question in webform.get_yesnofields().items():
            question_values[key] = question.data
        for key, filefield in webform.get_filefields().items():
            if filefield.data:
                # Save uploaded file; use filename as value
                filename = uploads.add(
                    filefield.data,
                    webform.school.data,
                    key,
                )
                question_filenames[const.form.FILE_PREFIX + key] = filename

        # Create database entry
        new_id = database.addapplication(
            **input_values,
            **question_values,
            **question_filenames,
        )

        # Send confirmation mail
        from  threading import Thread
        from . import mail

        send_mail = mail.available()
        if send_mail:
            Thread(
                target=mail.send_confirmation,
                kwargs={
                    'recipient': webform.email.data,
                    'config': settings,
                    'data': input_values,
                },
            ).start()

        # Return status message with database entry ID
        return jsonify({
            const.api.STATUS_KEY: const.api.PASS_VALUE,
            const.api.ID_KEY: new_id,
            const.api.MAIL_KEY: send_mail,
        })

    else:
        # Return status message with validation errors
        return jsonify({
            const.api.STATUS_KEY: const.api.FAIL_VALUE,
            const.api.ERROR_KEY: webform.errors
        })