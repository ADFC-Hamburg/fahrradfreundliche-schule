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
    upload_campaign_organizing = FileField(
    )
    upload_campaign_participation = FileField(
    )
    upload_compass = FileField(
    )
    upload_coordinator = FileField(
    )
    upload_lessons = FileField(
    )
    upload_parking = FileField(
    )
    upload_repairs = FileField(
    )
    upload_routemap = FileField(
    )
    #endregion

    #region Methods for grouping input fields
    def get_inputfields(self) -> tuple[Field, ...]:
        """Return input fields for personal and school information."""
        return (self.firstname,self.lastname,self.email,
                self.school,self.phone,self.address,
                self.zipcode,self.city,self.headcount)

    def get_questionfields(self) -> tuple[tuple[Field, FileField], ...]:
        """Return ordered input fields for questionnaire
        and corresponding input fields for file uploads."""
        return (
            (self.coordinator, self.upload_coordinator),
            (self.compass, self.upload_compass),
            (self.routemap, self.upload_routemap),
            (self.parking, self.upload_parking),
            (self.repairs, self.upload_repairs),
            (self.campaign_organizing, self.upload_campaign_organizing),
            (self.campaign_participation, self.upload_campaign_participation),
            (self.lessons, self.upload_lessons),
        )
    #endregion
