"""
Module defining URL paths for a flask app
and for rendering content.
"""

# Imports
from flask import abort, Blueprint, jsonify, render_template, request, send_file

from . import config, const, database, uploads, forms, paths

# Constants
_BLUEPRINT_NAME = 'pages'
_STATIC_ENDPOINT = _BLUEPRINT_NAME + '.static'

# Routes
pages = Blueprint(_BLUEPRINT_NAME, __name__,
                  template_folder=paths.TEMPLATES,
                  static_folder=paths.STATIC,
                  static_url_path='/static')
pages.add_app_template_filter(config.applytimezone, 'applytimezone')

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
        'form.html.j2', **_CONTEXT,
        form = webform,
        cert = settings[const.conf.keys.CERT],
        contact = settings[const.conf.keys.CONTACT],
        custom = settings[const.conf.keys.WEBSITE],
        uploads = settings[const.conf.keys.FORM][const.conf.keys.UPLOADS]
    )

@pages.route('/viewer/<int:id>')
def show_application(id: int):
    row = database.getapplication(id)
    if not row:
        abort(404, description=const.api.IDNOTFOUND_MESSAGE)
    settings = config.fetch()

    return render_template(
        'viewer/entry.html.j2', **_CONTEXT,
        row = row,
        settings = settings,
        file_prefix = const.form.FILE_PREFIX,
        questions = const.viewer.CRITERIA_SORTED,
    )

@pages.route('/api/submit', methods=['POST'])
def submit_application():
    settings = config.fetch()

    questioncount = len(settings[const.conf.keys.FORM][const.conf.keys.QUESTIONS][const.conf.keys.LIST])
    maxsize_file = settings[const.conf.keys.FORM][const.conf.keys.UPLOADS][const.conf.keys.FILESIZE]
    request.max_content_length = max(maxsize_file * questioncount, 1) * 1024 * 1024

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

@pages.route('/api/delete/<int:id>', methods=['POST'])
def delete_application(id: int):
    filenames = tuple(database.getfilenamedict(id).values())
    if database.deleteapplication(id):
        # Successful deletion; also delete dangling files
        from threading import Thread
        Thread(
            target=uploads.deletedanglingfiles,
            args=filenames,
        ).start()
        return jsonify({
            const.api.STATUS_KEY: const.api.PASS_VALUE,
        })
    else:
        return jsonify({
            const.api.STATUS_KEY: const.api.FAIL_VALUE,
            const.api.SINGLE_ERROR_KEY: const.api.IDNOTFOUND_MESSAGE,
        }), 404

@pages.route('/api/download/<int:id>/<field>')
def download_file(id: int, field: str):
    if field not in const.viewer.FILENAMES.keys():
        abort(404)

    filenamefield = const.form.FILE_PREFIX + field
    row = database.getapplication(id, filenamefield)
    if not row:
        abort(404, description=const.api.IDNOTFOUND_MESSAGE)
    if not row[filenamefield]:
        abort(404, description=const.api.FILENOTFOUND_MESSAGE)

    return send_file(
        uploads.getpath(row[filenamefield]),
        as_attachment=True,
        download_name=uploads.namefileforuser(field, row[filenamefield]),
    )

@pages.route('/api/download/<int:id>')
def download_archive(id: int):

    row = database.getapplication(id)
    if not row:
        abort(404, description=const.api.IDNOTFOUND_MESSAGE)

    archivename = ''.join((
        const.viewer.ARCHIVE_PREFIX,
        row['school'] or str(id),
        '.zip'
    ))

    from io import BytesIO
    import zipfile
    zipbuffer = BytesIO()
    with zipfile.ZipFile(zipbuffer, 'a', zipfile.ZIP_DEFLATED, False) as zfile:

        # Text summary
        zfile.writestr(const.viewer.SUMMARY_FILENAME + '.txt', database.summarize(row))

        # Uploaded files
        for field in const.viewer.FILENAMES.keys():
            filename = row[const.form.FILE_PREFIX + field]
            if not filename:
                continue
            zfile.write(
                uploads.getpath(filename),
                uploads.namefileforuser(field, filename),
            )

    zipbuffer.seek(0)
    return send_file(
        zipbuffer,
        as_attachment=True,
        download_name=archivename,
    )