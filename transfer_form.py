from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError
from wtforms.fields import IntegerField, DecimalField, SubmitField, SelectField
from wtforms.validators import InputRequired, NumberRange



class transfer_form(FlaskForm):
    source_account_number = SelectField('FROM:', choices=[], validators=[InputRequired()])
    destination_account_number = SelectField('TO:', choices=[], validators=[InputRequired()])
    amount = DecimalField('AMOUNT:', validators=[InputRequired(), NumberRange(min=1, max=100000)])
    submit = SubmitField('Submit')