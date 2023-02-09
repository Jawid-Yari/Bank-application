from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError
from wtforms.fields import IntegerField, DecimalField, SubmitField, SelectField
from wtforms.validators import InputRequired, NumberRange


class authentication_form(FlaskForm):
    nationalId = StringField("National ID", validators= [validators.InputRequired()])
    transaction_type = SelectField('Transaction Type', choices=[('withdraw', 'Withdraw'), ('deposit', 'Deposit'), ('transfer', 'Transfer')], validators=[InputRequired()])
    submit= SubmitField("submit")