from flask.ext.wtf import Form
from wtforms import TextAreaField, SubmitField, StringField, validators, ValidationError, PasswordField


class ContactForm(Form):
    name = StringField("Name", [validators.required("Please enter your name")])
    email = StringField("Email", [validators.required], [validators.email("Please enter a valid email address")])
    subject = StringField("Subject", [validators.required("Please enter a subject")])
    message = TextAreaField("Message", [validators.required("Please fill in your message.")])
    submit = SubmitField("Send")


class SigninForm(Form):
    username = StringField("Username", [validators.required])
    password = PasswordField("Password", [validators.required])
