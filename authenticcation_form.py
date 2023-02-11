from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError
from wtforms.fields import IntegerField, DecimalField, SubmitField, SelectField
from wtforms.validators import InputRequired, NumberRange


class authentication_form(FlaskForm):
    nationalId = StringField("NATIONAL ID:", validators= [validators.InputRequired()])
    transaction_type = SelectField('TRANSACTION TYPE:', choices=[('withdraw', 'Withdraw'), ('deposit', 'Deposit'), ('transfer', 'Transfer')], validators=[InputRequired()])
    submit= SubmitField("submit")