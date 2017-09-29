from wtforms import Form, BooleanField, StringField, PasswordField, validators, SelectField, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo


class SigninForm(Form):
    username = StringField("Username", [validators.required])
    password = PasswordField("Password", [validators.required])
