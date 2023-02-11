from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError
from wtforms.fields import IntegerField, DecimalField, SubmitField, SelectField
from wtforms.validators import InputRequired, NumberRange





class deposit_form(FlaskForm):
    account_number = SelectField('Account Number', choices=[], validators=[InputRequired()])
    amount = DecimalField('Deposit Amount', validators=[InputRequired(), NumberRange(min=1, max=50000)])
    submit = SubmitField('Submit')
