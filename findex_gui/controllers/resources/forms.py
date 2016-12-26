from wtforms import Form, BooleanField, StringField, PasswordField, validators, SelectField, IntegerField
from findex_common.static_variables import FileProtocols, user_agent


class ResourceForm(Form):
    server_name = StringField("Name", [validators.Length(min=4, max=25)])
    description = StringField("Description")
    server_address = StringField("Address/Hostname")
    resource_port = IntegerField("Port")
    resource_protocol = SelectField("Protocol", choices=[(v, k) for k, v in FileProtocols().data.iteritems()])
    basepath = StringField("Basepath", default="/")
    display_url = StringField("Display URL", default="")

    recursive_sizes = BooleanField("Recursive directory sizes", default=True)
    throttle_connections = IntegerField("Throttle connections (seconds)", default=0)

    web_user_agent = StringField("User Agent", default=user_agent)
    auth_user = StringField("Authentication Username")
    auth_pass = StringField("Authentication Password")
    auth_type = SelectField("Authentication", choices=[
        (0, "Default"),
        (1, "HTTP DIGEST"),
    ])
