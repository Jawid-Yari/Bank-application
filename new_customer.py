from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError
from wtforms.fields import IntegerField, DecimalField, SubmitField, SelectField, DateField
from wtforms.validators import InputRequired, NumberRange





class create_new_customer(FlaskForm):
    GivenName= StringField('Name:', validators=[InputRequired()])
    Surname= StringField('Surename:', validators=[InputRequired()])
    Streetaddress= StringField('Address:', validators=[InputRequired()])
    City= StringField('City:', validators=[InputRequired()])
    Zipcode= StringField('Zip Code:', validators=[InputRequired()])
    Country= StringField('Country:', validators=[InputRequired()])
    CountryCode = StringField('Country Code:', validators=[InputRequired()])
    Birthday= DateField('Birth Date:', validators=[InputRequired()])
    NationalId = StringField('National ID:', validators=[InputRequired()])
    TelephoneCountryCode = IntegerField('Telephone Country Code', validators=[validators.InputRequired()])
    Telephone = StringField('Phone Number', validators=[InputRequired()])
    EmailAddress = StringField('Email', validators=[InputRequired()])
    submit = SubmitField('Create')
