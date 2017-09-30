from findex_common.static_variables import FileProtocols, user_agent
from wtforms import TextAreaField, SubmitField, Form, BooleanField, StringField, PasswordField, validators, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo


class FormServerAddOptions(Form):
    basepath = StringField("Basepath", default="/", validators=[DataRequired()])
    display_url = StringField("Display URL", default="")

    recursive_sizes = BooleanField("Recursive directory sizes", default=True)
    throttle_connections = IntegerField("Throttle connections (seconds)", default=-1)
    user_agent = StringField("User Agent", default=user_agent)


class FormServerAddAuthentication(Form):
    auth_user = StringField("Username")
    auth_pass = StringField("Password")
    auth_type = SelectField("Authentication", choices=[
        (0, "Default"),
        (1, "HTTP DIGEST"),
    ])


class FormServerAdd(Form):
    server_name = StringField("Name", [validators.Length(min=4, max=25)])
    server_address = StringField("Address/Hostname", [DataRequired()])
    resource_port = IntegerField("Port", default=21)
    resource_protocol = SelectField("Protocol", validators=[DataRequired()], choices=sorted([(v, k.upper()) for k, v in FileProtocols().data.items()]))
