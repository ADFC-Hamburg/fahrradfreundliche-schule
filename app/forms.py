from flask_wtf import FlaskForm
from wtforms import Field, FileField, IntegerField, RadioField, StringField
import wtforms.validators as validators

from . import const

class ApplicationForm(FlaskForm):

    #region Input fields for personal and school information
    firstname = StringField(
        const.form.INPUTFIELDS_LABELS['firstname'],
        validators=[
            validators.InputRequired(),
        ],
    )
    lastname = StringField(
        const.form.INPUTFIELDS_LABELS['lastname'],
        validators=[
            validators.InputRequired(),
        ],
    )
    email = StringField(
        const.form.INPUTFIELDS_LABELS['email'],
        validators=[
            validators.InputRequired(),
        ],
    )
    school = StringField(
        const.form.INPUTFIELDS_LABELS['school'],
        validators=[
            validators.InputRequired(),
        ],
    )
    phone = StringField(
        const.form.INPUTFIELDS_LABELS['phone'],
        validators=[
            validators.InputRequired(),
            validators.Regexp(
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
            validators.InputRequired(),
        ],
    )
    zipcode = StringField(
        const.form.INPUTFIELDS_LABELS['zipcode'],
        validators=[
            validators.InputRequired(),
            validators.Length(
                min=const.form.ZIP_DIGITS,
                max=const.form.ZIP_DIGITS,
            ),
            validators.Regexp(
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
            validators.InputRequired(),
        ],
    )
    headcount = IntegerField(
        const.form.INPUTFIELDS_LABELS['headcount'],
        validators=[
            validators.InputRequired(),
            validators.NumberRange(
                min=0,
                max=const.form.HEADCOUNT_MAX,
            ),
        ],
    )
    #endregion

    #region Input fields for yes/no questions
    _YESNOCHOICES = ((1,const.form.CHOICE_YES),(0,const.form.CHOICE_NO))

    campaign_organizing = RadioField(
        const.form.QUESTIONS_LABELS['campaign_organizing'],
        choices = _YESNOCHOICES,
    )
    campaign_participation = RadioField(
        const.form.QUESTIONS_LABELS['campaign_participation'],
        choices = _YESNOCHOICES,
    )
    compass = RadioField(
        const.form.QUESTIONS_LABELS['compass'],
        choices = _YESNOCHOICES,
    )
    coordinator = RadioField(
        const.form.QUESTIONS_LABELS['coordinator'],
        choices = _YESNOCHOICES,
    )
    lessons = RadioField(
        const.form.QUESTIONS_LABELS['lessons'],
        choices = _YESNOCHOICES,
    )
    parking = RadioField(
        const.form.QUESTIONS_LABELS['parking'],
        choices = _YESNOCHOICES,
    )
    repairs = RadioField(
        const.form.QUESTIONS_LABELS['repairs'],
        choices = _YESNOCHOICES,
    )
    routemap = RadioField(
        const.form.QUESTIONS_LABELS['routemap'],
        choices = _YESNOCHOICES,
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
