from wtforms import Form, BooleanField, StringField, PasswordField, validators, SelectField, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo


class NmapRuleAdd(Form):
    name = StringField("Rule Name", [DataRequired], default="")
    hosts = StringField("IP Address/Range", [DataRequired()], default="127.0.0.1/32")
    ports = StringField("Ports", default="21")
    interval = IntegerField("Scan Interval (seconds)", default=86400)
    group = SelectField("Group", [DataRequired()], choices=[])
