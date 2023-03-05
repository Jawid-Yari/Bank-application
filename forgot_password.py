from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators,SubmitField
from wtforms.validators import DataRequired, Email


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
   

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
                            validators=[
                            validators.DataRequired(),
                            validators.Length(min=6, message='Password must be at least 6 characters long'),
                            validators.EqualTo('confirm', message='Passwords must match')
                                        ])
    confirm = PasswordField('Confirm Password', validators=[validators.DataRequired()])
    