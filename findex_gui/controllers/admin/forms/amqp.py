from findex_common.static_variables import FileProtocols, user_agent
from wtforms import TextAreaField, SubmitField, Form, BooleanField, StringField, PasswordField, validators, SelectField, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo


# class FormServerAddOptions(Form):
#     basepath = StringField("Basepath", default="/", validators=[DataRequired()])
#     display_url = StringField("Display URL", default="")
#
#     recursive_sizes = BooleanField("Recursive directory sizes", default=True)
#     throttle_connections = IntegerField("Throttle connections (seconds)", default=0)
#     user_agent = StringField("User Agent", default=user_agent)
#
#
# class FormServerAddAuthentication(Form):
#     auth_user = StringField("Username")
#     auth_pass = StringField("Password")
#     auth_type = SelectField("Authentication", choices=[
#         (0, "Default"),
#         (1, "HTTP DIGEST"),
#     ])
#
#
# class SigninForm(Form):
#     username = StringField("Username", [validators.required])
#     password = PasswordField("Password", [validators.required])


class FormAmqpAdd(Form):
    broker = RadioField("Broker", choices=[('rabbitmq', 'RabbitMQ')], default='rabbitmq')
    name = StringField("Name", [DataRequired()])
    address = StringField("Host", [DataRequired()])
    port = StringField("Port", [DataRequired()], default=5672)
    user = StringField("Username", [DataRequired()])
    passwd = StringField("Password", [DataRequired()])
    vhost = StringField("Vhost", [DataRequired()], default='indexer')
    queue = StringField("Queue name", [DataRequired()], default='indexer')
