from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError
from wtforms.fields import IntegerField, DecimalField, SubmitField, SelectField
from wtforms.validators import InputRequired, NumberRange



class transfer_form(FlaskForm):
    source_account_number = SelectField('From', choices=[], validators=[InputRequired()])
    destination_account_number = SelectField('To', choices=[], validators=[InputRequired()])
    amount = DecimalField('Amount to transfer', validators=[InputRequired(), NumberRange(min=1, max=100000)])
    submit = SubmitField('Submit')