from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError
from wtforms.fields import IntegerField, DecimalField, SubmitField, SelectField
from wtforms.validators import InputRequired, NumberRange


class deposit_form1(FlaskForm):
    nationalId = StringField("National ID", validators= [validators.InputRequired()])
    submit= SubmitField("submit")




class deposit_form(FlaskForm):
    account_number = SelectField('Account Number', choices=[], validators=[InputRequired()])
    amount = DecimalField('Deposit Amount', validators=[InputRequired(), NumberRange(min=0, max=5000)])
    submit = SubmitField('Submit')