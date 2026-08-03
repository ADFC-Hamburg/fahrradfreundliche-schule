from collections.abc import Iterable

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileSize
from wtforms import Field, BooleanField, EmailField, HiddenField, IntegerField, PasswordField, RadioField, StringField, SubmitField, TelField
import wtforms.validators as validators

from . import const

keys = const.conf.keys


class ConditionalInputRequired(validators.InputRequired):
    """A validator which makes a field required, but skips validation
    if the field has flags.skip_validation set to True."""

    def __call__(self,form,field):
        if not field.flags.skip_validation:
            super().__call__(form, field)

class FileRequiredIfLinkDataMatch(FileRequired):
    """Validates that one or multiple files have been uploaded
    if the data of another field matches a list of desired values.

    The other field is read from the link attribute of the field
    to be validated."""

    def __init__(self, message=None, target:Iterable = ()):
        self.message = message
        self.field_flags = {"required": False}
        self.target = target

    def __call__(self, form, field):
        if hasattr(field, 'link') and field.link.data in self.target:
            super().__call__(form, field)

class MediatypeAllowed():
    """Validates that the uploaded file(s) is allowed by a given list
    of media types."""

    def __init__(self, mediatypes:Iterable[str, ...], message=None):
        self.message = message
        self.allowed_types = mediatypes
    
    def __call__(self, form, field):
        from magic import from_buffer as magic_from_buffer
        from werkzeug.datastructures import FileStorage

        field_data = (field.data,) if not isinstance(field.data, list) else field.data
        if not (
            all(isinstance(x, FileStorage) and x for x in field_data) and field_data
        ):
            return
        
        for f in field_data:
            previous_position = f.stream.tell()
            mediatype = magic_from_buffer(f.read(), mime=True)
            f.stream.seek(previous_position)
            if not mediatype in self.allowed_types:
                raise validators.StopValidation(
                    self.message or
                    ('File does not have an approved media type: '
                    + ', '.join(self.allowed_types))
                )

class ApplicationForm(FlaskForm):

    #region Static methods
    @staticmethod
    def format_mediatypes_from_config(formconfig: dict) -> str:
        """Reads allowed media types from a form configuration and
        formats the list of allowed media types as a string."""
        from mimetypes import guess_extension

        mediatypes = formconfig[keys.UPLOADS][keys.MEDIATYPE]
        extensions = tuple(guess_extension(t)[1:].upper() for t in mediatypes)
        if not extensions:
            return ''
        if len(extensions) == 1:
            return extensions[0]
        return const.form.LIST_SEPARATOR_LAST.join((
            const.form.LIST_SEPARATOR.join(extensions[:-1]),
            extensions[-1]
        ))
    #endregion

    #region Input fields for personal and school information
    _FIELD_REQUIRED_VALIDATOR = validators.InputRequired(message=const.form.ERROR_REQUIRED)

    firstname = StringField(
        const.form.INPUTFIELDS_LABELS['firstname'],
        validators=[
            _FIELD_REQUIRED_VALIDATOR,
        ],
    )
    lastname = StringField(
        const.form.INPUTFIELDS_LABELS['lastname'],
        validators=[
            _FIELD_REQUIRED_VALIDATOR,
        ],
    )
    email = EmailField(
        const.form.INPUTFIELDS_LABELS['email'],
        validators=[
            _FIELD_REQUIRED_VALIDATOR,
            validators.Email(
                message=const.form.ERROR_INVALID,
            ),
        ],
    )
    school = StringField(
        const.form.INPUTFIELDS_LABELS['school'],
        validators=[
            _FIELD_REQUIRED_VALIDATOR,
        ],
    )
    phone = TelField(
        const.form.INPUTFIELDS_LABELS['phone'],
        validators=[
            _FIELD_REQUIRED_VALIDATOR,
            validators.Regexp(
                message=const.form.ERROR_INVALID,
                regex=const.form.PHONE_REGEX,
            ),
        ],
        render_kw={
            'pattern': const.form.PHONE_PATTERN,
        },
    )
    address = StringField(
        const.form.INPUTFIELDS_LABELS['address'],
        validators=[
            _FIELD_REQUIRED_VALIDATOR,
        ],
    )
    zipcode = StringField(
        const.form.INPUTFIELDS_LABELS['zipcode'],
        validators=[
            _FIELD_REQUIRED_VALIDATOR,
            validators.Length(
                message=const.form.ERROR_LENGTH_ZIPCODE,
                min=const.form.ZIP_DIGITS,
                max=const.form.ZIP_DIGITS,
            ),
            validators.Regexp(
                message=const.form.ERROR_INVALID,
                regex=const.form.ZIP_REGEX,
            ),
        ],
        render_kw={
            'pattern': const.form.ZIP_PATTERN,
        },
    )
    city = StringField(
        const.form.INPUTFIELDS_LABELS['city'],
        validators=[
            _FIELD_REQUIRED_VALIDATOR,
        ],
    )
    headcount = IntegerField(
        const.form.INPUTFIELDS_LABELS['headcount'],
        validators=[
            _FIELD_REQUIRED_VALIDATOR,
            validators.NumberRange(
                message=const.form.ERROR_INVALID,
                min=0,
                max=const.form.HEADCOUNT_MAX,
            ),
        ],
    )
    #endregion

    #region Input fields for yes/no questions
    _YESNOCHOICES = ((1,const.form.CHOICE_YES),(0,const.form.CHOICE_NO))
    _YESNO_REQUIRED_VALIDATOR = ConditionalInputRequired(message=const.form.ERROR_REQUIRED_YESNO)
    _YESNO_COMMON_ARGS = {
        'choices': _YESNOCHOICES,
        'validators': [
            _YESNO_REQUIRED_VALIDATOR,
        ],
    }

    campaign_organizing = RadioField(
        const.form.QUESTIONS_LABELS['campaign_organizing'],
        **_YESNO_COMMON_ARGS,
    )
    campaign_participation = RadioField(
        const.form.QUESTIONS_LABELS['campaign_participation'],
        **_YESNO_COMMON_ARGS,
    )
    compass = RadioField(
        const.form.QUESTIONS_LABELS['compass'],
        **_YESNO_COMMON_ARGS,
    )
    coordinator = RadioField(
        const.form.QUESTIONS_LABELS['coordinator'],
        **_YESNO_COMMON_ARGS,
    )
    lessons = RadioField(
        const.form.QUESTIONS_LABELS['lessons'],
        **_YESNO_COMMON_ARGS,
    )
    parking = RadioField(
        const.form.QUESTIONS_LABELS['parking'],
        **_YESNO_COMMON_ARGS,
    )
    repairs = RadioField(
        const.form.QUESTIONS_LABELS['repairs'],
        **_YESNO_COMMON_ARGS,
    )
    routemap = RadioField(
        const.form.QUESTIONS_LABELS['routemap'],
        **_YESNO_COMMON_ARGS,
    )
    #endregion

    #region Input fields for file uploads
    _FILE_MAYBE_REQUIRED_VALIDATOR = FileRequiredIfLinkDataMatch(
        message = const.form.ERROR_REQUIRED_FILE,
        target = (True, 1, '1'),
    )
    _FILESIZE_DEFAULT_VALIDATOR = FileSize(
        message = const.form.ERROR_FILESIZE % const.conf.FORM_DEFAULT[keys.UPLOADS][keys.FILESIZE],
        max_size = const.conf.FORM_DEFAULT[keys.UPLOADS][keys.FILESIZE] * 1024 * 1024
    )
    _MEDIATYPE_DEFAULT_VALIDATOR = MediatypeAllowed(
        message = const.form.ERROR_MEDIATYPE % format_mediatypes_from_config(const.conf.FORM_DEFAULT),
        mediatypes = const.conf.FORM_DEFAULT[keys.UPLOADS][keys.MEDIATYPE],
    )
    _FILEFIELD_DEFAULT_VALIDATORS = (
        _FILE_MAYBE_REQUIRED_VALIDATOR,
        _FILESIZE_DEFAULT_VALIDATOR,
        _MEDIATYPE_DEFAULT_VALIDATOR,
    )
    _FILEFIELD_DEFAULT_RENDER_KW = {
        'accept': ', '.join(const.conf.FORM_DEFAULT[keys.UPLOADS][keys.MEDIATYPE]),
        'data-maxsize': str(_FILESIZE_DEFAULT_VALIDATOR.max_size),
    }

    file_campaign_organizing = FileField(
        validators = _FILEFIELD_DEFAULT_VALIDATORS,
        render_kw = _FILEFIELD_DEFAULT_RENDER_KW,
    )
    file_campaign_participation = FileField(
        validators = _FILEFIELD_DEFAULT_VALIDATORS,
        render_kw = _FILEFIELD_DEFAULT_RENDER_KW,
    )
    file_compass = FileField(
        validators = _FILEFIELD_DEFAULT_VALIDATORS,
        render_kw = _FILEFIELD_DEFAULT_RENDER_KW,
    )
    file_coordinator = FileField(
        validators = _FILEFIELD_DEFAULT_VALIDATORS,
        render_kw = _FILEFIELD_DEFAULT_RENDER_KW,
    )
    file_lessons = FileField(
        validators = _FILEFIELD_DEFAULT_VALIDATORS,
        render_kw = _FILEFIELD_DEFAULT_RENDER_KW,
    )
    file_parking = FileField(
        validators = _FILEFIELD_DEFAULT_VALIDATORS,
        render_kw = _FILEFIELD_DEFAULT_RENDER_KW,
    )
    file_repairs = FileField(
        validators = _FILEFIELD_DEFAULT_VALIDATORS,
        render_kw = _FILEFIELD_DEFAULT_RENDER_KW,
    )
    file_routemap = FileField(
        validators = _FILEFIELD_DEFAULT_VALIDATORS,
        render_kw = _FILEFIELD_DEFAULT_RENDER_KW,
    )
    #endregion

    #region Checkboxes for consent
    _CONSENT_REQUIRED_VALIDATOR = validators.InputRequired(message=const.form.ERROR_REQUIRED_CONSENT)

    privacy_consent = BooleanField(
        validators=[
            _CONSENT_REQUIRED_VALIDATOR,
        ],
    )
    storage_consent = BooleanField(
        validators=[
            _CONSENT_REQUIRED_VALIDATOR,
        ],
    )
    #endregion

    def __init__(self, formconfig: None | dict = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = formconfig
        self.inputfields = (
            self.firstname,self.lastname,self.email,
            self.school,self.phone,self.address,
            self.zipcode,self.city,self.headcount,
        )
        self.questions = {
            'campaign_organizing': (self.campaign_organizing, self.file_campaign_organizing),
            'campaign_participation': (self.campaign_participation, self.file_campaign_participation),
            'compass': (self.compass, self.file_compass),
            'coordinator': (self.coordinator, self.file_coordinator),
            'lessons': (self.lessons, self.file_lessons),
            'parking': (self.parking, self.file_parking),
            'repairs': (self.repairs, self.file_repairs),
            'routemap': (self.routemap, self.file_routemap),
        }
        self.yesnofields = {key: fields[0] for key, fields in self.questions.items()}
        self.filefields = {key: fields[1] for key, fields in self.questions.items()}

        for key in self.questions.keys():
            # Link upload to question (for FileRequiredIfLinkDataMatch validator)
            self.filefields[key].link = self.yesnofields[key]

        if formconfig:
            # Apply settings
            if not self.zipcode.data:
                self.zipcode.data = formconfig[keys.DEFAULT][keys.ZIPCODE]
            if not self.city.data:
                self.city.data = formconfig[keys.DEFAULT][keys.CITY]
            for key, question in self.get_yesnofields().items():
                if not formconfig[keys.QUESTIONS][const.conf.questionkeys[key]]:
                    # Do not verify unused fields
                    question.flags.skip_validation = True
                    question.validate_choice = False

            # Replace filefield validators and other settings
            filefield_validators = []
            if formconfig[keys.UPLOADS][keys.REQUIRED]:
                filefield_validators.append(self._FILE_MAYBE_REQUIRED_VALIDATOR)
            if formconfig[keys.UPLOADS][keys.FILESIZE] == const.conf.FORM_DEFAULT[keys.UPLOADS][keys.FILESIZE]:
                filefield_maxsize = self._FILESIZE_DEFAULT_VALIDATOR.max_size
                filefield_validators.append(self._FILESIZE_DEFAULT_VALIDATOR)
            elif formconfig[keys.UPLOADS][keys.FILESIZE]:
                filefield_maxsize = int(float(formconfig[keys.UPLOADS][keys.FILESIZE]) * 1024 * 1024)
                filefield_validators.append(FileSize(
                    message = const.form.ERROR_FILESIZE % formconfig[keys.UPLOADS][keys.FILESIZE],
                    max_size = filefield_maxsize
                ))
            else:
                filefield_maxsize = None
            if formconfig[keys.UPLOADS][keys.MEDIATYPE] == const.conf.FORM_DEFAULT[keys.UPLOADS][keys.MEDIATYPE]:
                filefield_validators.append(self._MEDIATYPE_DEFAULT_VALIDATOR)
            elif formconfig[keys.UPLOADS][keys.MEDIATYPE]:
                filefield_validators.append(MediatypeAllowed(
                    message = const.form.ERROR_MEDIATYPE % self.format_mediatypes_from_config(formconfig),
                    mediatypes = formconfig[keys.UPLOADS][keys.MEDIATYPE],
                ))
            filefield_render_kw = {
                'accept': ', '.join(formconfig[keys.UPLOADS][keys.MEDIATYPE]),
                'data-maxsize': str(filefield_maxsize) if filefield_maxsize else '',
                'data-neverrequired': 'true' if not formconfig[keys.UPLOADS][keys.REQUIRED] else 'false',
            }
            for filefield in self.get_filefields().values():
                filefield.validators = filefield_validators
                filefield.render_kw = filefield_render_kw

    #region Methods for grouping input fields
    def get_inputfields(self) -> tuple[Field, ...]:
        """Return input fields for personal and school information."""
        return self.inputfields

    def get_questionfields(self) -> tuple[tuple[Field, FileField], ...]:
        """Return ordered input fields for questionnaire
        and corresponding input fields for file uploads."""
        if self.config:
            order = (field for field, confkey in const.conf.questionkeys.items() if self.config[keys.QUESTIONS][confkey])
        else:
            order = (field for field, confkey in const.conf.questionkeys.items() if const.conf.FORM_DEFAULT[keys.QUESTIONS][confkey])
        return tuple(self.questions[key] for key in order)
    
    def get_fields(self) -> tuple[Field, ...]:
        """Return all fields in this form."""
        return(
            self.csrf_token,
            *self.get_inputfields(),
            *(field for question in self.questions.values() for field in question),
        )

    def get_yesnofields(self) -> dict[str, RadioField]:
        """Return input fields for questionnaire."""
        return self.yesnofields

    def get_filefields(self) -> dict[str, FileField]:
        """Return input fields for file uploads."""
        return self.filefields
    #endregion

class LoginForm(FlaskForm):
    _FIELD_REQUIRED_VALIDATOR = validators.InputRequired(message=const.users.ERROR_EMPTY)
    username = StringField(
        label=const.users.LABELS['username'],
        validators=[
            _FIELD_REQUIRED_VALIDATOR,
        ]
    )
    password = PasswordField(
        label=const.users.LABELS['password'],
        validators=[
            _FIELD_REQUIRED_VALIDATOR,
        ]
    )
    submit = SubmitField(
        label=const.users.LABELS['submit'],
    )

class AccountForm(LoginForm):
    admin_permission = BooleanField(
        label=const.users.LABELS['admin'],
    )
    delete_permission = BooleanField(
        label=const.users.LABELS['delete'],
    )
    submit = SubmitField(
        label=const.users.LABELS['submit_edit'],
    )

class AccountEditForm(AccountForm):
    _OPTIONAL_VALIDATOR = validators.Optional()
    username = StringField(
        label=const.users.LABELS['username'],
        validators=[
            _OPTIONAL_VALIDATOR,
        ]
    )
    password = PasswordField(
        label=const.users.LABELS['password'],
        validators=[
            _OPTIONAL_VALIDATOR,
        ]
    )
    target_id = HiddenField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if kwargs.get(const.users.keys.ID):
            self.target_id.data = str(kwargs.get(const.users.keys.ID))
        if kwargs.get(const.users.keys.NAME):
            self.username.data = str(kwargs.get(const.users.keys.NAME))
        if kwargs.get(const.users.PERMISSIONS.ADMIN):
            self.admin_permission.default = self.admin_permission.data = bool(kwargs.get(const.users.PERMISSIONS.ADMIN))
        if kwargs.get(const.users.PERMISSIONS.DELETE):
            self.delete_permission.data = bool(kwargs.get(const.users.PERMISSIONS.DELETE))