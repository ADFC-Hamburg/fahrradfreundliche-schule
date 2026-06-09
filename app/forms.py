from flask_wtf import FlaskForm
from wtforms import Field, IntegerField, StringField
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
        ],
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
        ],
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
        ],
    )
    #endregion

    #region Methods for grouping input fields
    def get_inputfields(self) -> tuple[Field, ...]:
        """Return input fields for personal and school information."""
        return (self.firstname,self.lastname,self.email,
                self.school,self.phone,self.address,
                self.zipcode,self.city,self.headcount)
    #endregion
