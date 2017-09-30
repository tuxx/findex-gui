from wtforms import Form, BooleanField, StringField, PasswordField, validators, SelectField, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo


class FormAmqpAdd(Form):
    broker = RadioField("Broker", choices=[('rabbitmq', 'RabbitMQ')], default='rabbitmq')
    name = StringField("Name", [DataRequired()])
    address = StringField("Host", [DataRequired()])
    port = StringField("Port", [DataRequired()], default=5672)
    user = StringField("Username", [DataRequired()])
    passwd = StringField("Password", [DataRequired()])
    vhost = StringField("Vhost", [DataRequired()], default='indexer')
    queue = StringField("Queue name", [DataRequired()], default='indexer')