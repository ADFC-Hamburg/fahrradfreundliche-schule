from collections.abc import Iterable

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileSize
from wtforms import Field, BooleanField, EmailField, IntegerField, RadioField, StringField
import wtforms.validators as validators

from . import const

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
        
        mediatypes = tuple(magic_from_buffer(f.read(), mime=True) for f in field_data)
        if not all(t in self.allowed_types for t in mediatypes):
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

        mediatypes = formconfig[const.conf.UPLOADS_KEY][const.conf.MEDIATYPE_KEY]
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
    phone = StringField(
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
        message = const.form.ERROR_FILESIZE % const.conf.FORM_DEFAULT[const.conf.UPLOADS_KEY][const.conf.FILESIZE_KEY],
        max_size = const.conf.FORM_DEFAULT[const.conf.UPLOADS_KEY][const.conf.FILESIZE_KEY] * 1024 * 1024
    )
    _MEDIATYPE_DEFAULT_VALIDATOR = MediatypeAllowed(
        message = const.form.ERROR_MEDIATYPE % format_mediatypes_from_config(const.conf.FORM_DEFAULT),
        mediatypes = const.conf.FORM_DEFAULT[const.conf.UPLOADS_KEY][const.conf.MEDIATYPE_KEY],
    )
    _FILEFIELD_DEFAULT_VALIDATORS = (
        _FILE_MAYBE_REQUIRED_VALIDATOR,
        _FILESIZE_DEFAULT_VALIDATOR,
        _MEDIATYPE_DEFAULT_VALIDATOR,
    )
    _FILEFIELD_DEFAULT_RENDER_KW = {
        'accept': ', '.join(const.conf.FORM_DEFAULT[const.conf.UPLOADS_KEY][const.conf.MEDIATYPE_KEY]),
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

        for fields in self.questions.values():
            # Link upload to question (for FileRequiredIfLinkDataMatch validator)
            fields[1].link = fields[0]

        if formconfig:
            # Apply settings
            if not self.zipcode.data:
                self.zipcode.data = formconfig[const.conf.DEFAULT_KEY][const.conf.ZIPCODE_KEY]
            if not self.city.data:
                self.city.data = formconfig[const.conf.DEFAULT_KEY][const.conf.CITY_KEY]
            for key, fields in self.questions.items():
                if key not in formconfig[const.conf.QUESTIONS_KEY][const.conf.LIST_KEY]:
                    # Do not verify unused fields
                    fields[0].flags.skip_validation = True
                    fields[0].validate_choice = False

            # Replace filefield validators and other settings
            filefield_validators = [self._FILE_MAYBE_REQUIRED_VALIDATOR,]
            if formconfig[const.conf.UPLOADS_KEY][const.conf.FILESIZE_KEY] == const.conf.FORM_DEFAULT[const.conf.UPLOADS_KEY][const.conf.FILESIZE_KEY]:
                filefield_maxsize = self._FILESIZE_DEFAULT_VALIDATOR.max_size
                filefield_validators.append(self._FILESIZE_DEFAULT_VALIDATOR)
            elif formconfig[const.conf.UPLOADS_KEY][const.conf.FILESIZE_KEY]:
                filefield_maxsize = int(float(formconfig[const.conf.UPLOADS_KEY][const.conf.FILESIZE_KEY]) * 1024 * 1024)
                filefield_validators.append(FileSize(
                    message = const.form.ERROR_FILESIZE % formconfig[const.conf.UPLOADS_KEY][const.conf.FILESIZE_KEY],
                    max_size = filefield_maxsize
                ))
            else:
                filefield_maxsize = None
            if formconfig[const.conf.UPLOADS_KEY][const.conf.MEDIATYPE_KEY] == const.conf.FORM_DEFAULT[const.conf.UPLOADS_KEY][const.conf.MEDIATYPE_KEY]:
                filefield_validators.append(self._MEDIATYPE_DEFAULT_VALIDATOR)
            elif formconfig[const.conf.UPLOADS_KEY][const.conf.MEDIATYPE_KEY]:
                filefield_validators.append(MediatypeAllowed(
                    message = const.form.ERROR_MEDIATYPE % self.format_mediatypes_from_config(formconfig),
                    mediatypes = formconfig[const.conf.UPLOADS_KEY][const.conf.MEDIATYPE_KEY],
                ))
            filefield_render_kw = {
                'accept': ', '.join(formconfig[const.conf.UPLOADS_KEY][const.conf.MEDIATYPE_KEY]),
                'data-maxsize': str(filefield_maxsize) if filefield_maxsize else '',
            }
            for fields in self.questions.values():
                fields[1].validators = filefield_validators
                fields[1].render_kw = filefield_render_kw

    #region Methods for grouping input fields
    def get_inputfields(self) -> tuple[Field, ...]:
        """Return input fields for personal and school information."""
        return (self.firstname,self.lastname,self.email,
                self.school,self.phone,self.address,
                self.zipcode,self.city,self.headcount)

    def get_questionfields(self, formconfig: None | dict = None) -> tuple[tuple[Field, FileField], ...]:
        """Return ordered input fields for questionnaire
        and corresponding input fields for file uploads."""
        if self.config:
            order = self.config[const.conf.QUESTIONS_KEY][const.conf.LIST_KEY]
        else:
            order = const.form.QUESTIONS_LABELS.keys()
        return tuple(self.questions[key] for key in order)
    #endregion
