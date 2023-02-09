from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError
from wtforms.fields import IntegerField, DecimalField, SubmitField, SelectField
from wtforms.validators import InputRequired, NumberRange



class withdrawal_form(FlaskForm):
    account_number = SelectField('Account Number', choices=[], validators=[InputRequired()])
    amount = DecimalField('Wthdrawal Amount', validators=[InputRequired(), NumberRange(min=0, max=30000)])
    submit = SubmitField('Submit')