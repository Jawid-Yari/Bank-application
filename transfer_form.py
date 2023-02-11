from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError
from wtforms.fields import IntegerField, DecimalField, SubmitField, SelectField
from wtforms.validators import InputRequired, NumberRange



class withdrawal_form(FlaskForm):
    source_account_number = SelectField('From', choices=[], validators=[InputRequired()])
    destinatio_account_number = SelectField('From', choices=[], validators=[InputRequired()])
    amount = DecimalField('Deposit Amount', validators=[InputRequired(), NumberRange(min=1, max=100000)])
    submit = SubmitField('Submit')