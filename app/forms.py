from flask_wtf import FlaskForm
from wtforms import Field, BooleanField, EmailField, FileField, IntegerField, RadioField, StringField
import wtforms.validators as validators

from . import const

class ConditionalInputRequired(validators.InputRequired):
    """A validator which makes a field required, but skips validation
    if the field has flags.skip_validation set to True."""

    def __call__(self,form,field):
        if not field.flags.skip_validation:
            super().__call__(form, field)

class ApplicationForm(FlaskForm):

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
    file_campaign_organizing = FileField(
    )
    file_campaign_participation = FileField(
    )
    file_compass = FileField(
    )
    file_coordinator = FileField(
    )
    file_lessons = FileField(
    )
    file_parking = FileField(
    )
    file_repairs = FileField(
    )
    file_routemap = FileField(
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
