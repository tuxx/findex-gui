from findex_common.static_variables import FileProtocols, user_agent
from wtforms import TextAreaField, SubmitField, Form, BooleanField, StringField, PasswordField, validators, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo


class FormMqAdd(Form):
    name = StringField("Name", [DataRequired(), validators.Length(min=4, max=25)])
    host = StringField("Address/Hostname", [DataRequired()])
    port = IntegerField("Port", [DataRequired()], default=5672)
    broker = SelectField("Broker", choices=[
        ("rabbitmq", "RabittMQ"),
    ])
    vhost = StringField("Vhost", [DataRequired()])
    queue = StringField("Queue Name", [DataRequired()])
    ssl = BooleanField("SSL", default=False)
    auth_user = StringField("Username", [DataRequired()])
    auth_pass = StringField("Password", [DataRequired()])
