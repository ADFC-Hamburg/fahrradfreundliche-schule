"""
Module defining URL paths for a flask app
and for rendering content.
"""

# Imports
from functools import wraps

from flask import abort, Blueprint, jsonify, render_template, redirect, request, send_file, session, url_for

from . import config, const, database, uploads, forms, paths, protection


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
    'userkeys': const.users.keys,
    'userperms': const.users.PERMISSIONS,
    'version': const.app.VERSION
}


#region Login/logout routes
@pages.route('/login', methods=['GET', 'POST'])
@protection.block_repeated_attempts
def login():
    error = None

    loginform = forms.LoginForm()
    settings = config.fetch()

    if request.method == 'POST':
        if loginform.validate_on_submit():
            login_valid = protection.login_user(
                loginform.username.data,
                loginform.password.data
            )
            if login_valid:
                return redirect(url_for('pages.list_applications'))
            else:
                error = const.users.ERROR_INVALID
                protection.log_failed_login(request.remote_addr)
        else:
            error = const.users.ERROR_EMPTY

    return render_template(
        'viewer/login.html.j2', **_CONTEXT,
        error = error,
        form = loginform,
        settings = settings,
    )

@pages.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('pages.login'))
#endregion

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

#region Viewer routes
@pages.route('/viewer')
@protection.login_required
def list_applications():
    rows = database.getapplicationlist('id', 'school', 'timestamp', const.sql.FILECOUNT)
    settings = config.fetch()

    return render_template(
        'viewer/list.html.j2', **_CONTEXT,
        rows = rows,
        settings = settings,
    )

@pages.route('/viewer/<int:id>')
@protection.login_required
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

@pages.route('/viewer/accounts')
@protection.login_required
@protection.admin_required
def list_users():
    rows = database.getuserlist(
        const.users.keys.ID,
        const.users.keys.NAME,
        const.users.PERMISSIONS.ADMIN,
        const.users.PERMISSIONS.DELETE,
    )
    if 'edit' in request.args and request.args.get('edit').isdigit():
        row_to_edit = database.getuser(int(request.args.get('edit')))
    else:
        row_to_edit = None
    if row_to_edit:
        form = forms.AccountEditForm(
            **dict(row_to_edit)
        )
    else:
        form = forms.AccountForm()

    return render_template(
        'viewer/accounts.html.j2', **_CONTEXT,
        rows = rows,
        row_to_edit = row_to_edit,
        form = form,
    )
#endregion

#region Application API
@pages.route('/api/submit', methods=['POST'])
def submit_application():
    settings = config.fetch()

    questioncount = sum(bool(question) for question in settings[const.conf.keys.FORM][const.conf.keys.QUESTIONS].values())
    maxsize_file = settings[const.conf.keys.FORM][const.conf.keys.UPLOADS][const.conf.keys.FILESIZE]
    request.max_content_length = max(maxsize_file * questioncount, 1) * 1024 * 1024

    webform = forms.ApplicationForm(formconfig=settings[const.conf.keys.FORM])
    if webform.validate_on_submit():
        # Put all values into dictionaries
        input_values = {field.short_name: field.data
                        for field in webform.get_inputfields()}
        question_values = {}
        question_filenames = {}
        original_filenames = []
        for key, question in webform.get_yesnofields().items():
            question_values[key] = question.data
        for key, filefield in webform.get_filefields().items():
            if filefield.data:
                original_filenames.append(filefield.data.filename)
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
@protection.login_required
@protection.deletion_required
def delete_application(id: int):
    filenames = tuple(database.getfilenames(id).values())
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
@protection.login_required
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
@protection.login_required
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
#endregion

#region User account API
@pages.route('/api/users/add', methods=['POST'])
@protection.login_required
@protection.admin_required
def add_user():
    form = forms.AccountForm()
    if form.validate_on_submit:
        # Put all values into a dictionary
        values = {
            const.users.keys.NAME: form.username.data,
            const.users.keys.PASS: form.password.data,
            str(const.users.PERMISSIONS.ADMIN): form.admin_permission.data,
            str(const.users.PERMISSIONS.DELETE): form.delete_permission.data,
        }
        # Create database entry
        new_id = database.adduser(**values)
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

@pages.route('/api/users/edit/<int:id>', methods=['POST'])
@protection.login_required
@protection.admin_required
def edit_user(id: int):
    form = forms.AccountEditForm()
    if form.validate_on_submit:
        # Put all values into a dictionary
        values = {
            const.users.keys.NAME: form.username.data,
            const.users.keys.PASS: form.password.data,
            str(const.users.PERMISSIONS.ADMIN): form.admin_permission.data,
            str(const.users.PERMISSIONS.DELETE): form.delete_permission.data,
        }
        # Edit database entry
        if database.edituser(int(form.target_id.data),**values):
            # Return status message; update username if neccessary
            if id == session.get(const.users.keys.ID) and form.username.data:
                session[const.users.keys.NAME] = form.username.data
            return jsonify({
                const.api.STATUS_KEY: const.api.PASS_VALUE,
            })
        else:
            return jsonify({
                const.api.STATUS_KEY: const.api.FAIL_VALUE,
                const.api.SINGLE_ERROR_KEY: const.api.IDNOTFOUND_MESSAGE,
            }), 404
    else:
        # Return status message with validation errors
        return jsonify({
            const.api.STATUS_KEY: const.api.FAIL_VALUE,
            const.api.ERROR_KEY: webform.errors
        })

@pages.route('/api/users/delete/<int:id>', methods=['POST'])
@protection.login_required
@protection.admin_required
def delete_user(id: int):
    if database.deleteuser(id):
        return jsonify({
            const.api.STATUS_KEY: const.api.PASS_VALUE,
        })
    else:
        return jsonify({
            const.api.STATUS_KEY: const.api.FAIL_VALUE,
            const.api.SINGLE_ERROR_KEY: const.api.IDNOTFOUND_MESSAGE,
        }), 404
#endregion