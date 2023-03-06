from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError
from wtforms.fields import IntegerField, DecimalField, SubmitField, SelectField, DateField
from wtforms.validators import InputRequired, NumberRange


class get_customer_profile(FlaskForm):
    customer_id = IntegerField('Customer ID', validators=[InputRequired()])
    search = SubmitField('Search')
    