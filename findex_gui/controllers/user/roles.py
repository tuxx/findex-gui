import six
import sqlalchemy
import json
from flask import request

from sqlalchemy_utils.types.json import JSONType, has_postgres_json

from findex_common.exceptions import RoleException


role_mapping = {
    1: {
        "name": "RESOURCE_VIEW",
        "info": "Pages or resources may be accessed",
        "id": 1
    },
    2: {
        "name": "RESOURCE_CREATE",
        "info": "May create a new resource and a new server",
        "id": 2
    },
    3: {
        "name": "USER_CREATE_GROUP",
        "info": "May create an user group",
        "id": 3
    },
    4: {
        "name": "USER_CREATE",
        "info": "May create an user",
        "id": 4
    },
    5: {
        "name": "USER_DELETE",
        "info": "May delete an user",
        "id": 5
    },
    6: {
        "name": "USER_CREATE_ADMIN",
        "info": "May create an admin user",
        "id": 6
    },
    7: {
        "name": "USER_REGISTERED",
        "info": "User must be registered",
        "id": 7
    }
}


class Role:
    def __init__(self, *arg):
        self.rid = None
        self.name = None
        self.info = None
        if isinstance(arg[0], int):
            role = self.by_id(arg[0])
        elif isinstance(arg[0], str):
            role = self.by_name(arg[0])
        else:
            raise RoleException("unknown arg")
        self.rid = role["id"]
        self.name = role["name"]
        self.info = role["info"]

    @staticmethod
    def by_id(r_id):
        if not isinstance(r_id, int):
            raise RoleException("rid not an integer")
        if r_id not in role_mapping:
            raise RoleException("unknown role number \"%d\"" % r_id)
        return role_mapping[r_id]

    @staticmethod
    def by_name(r_name):
        for k, v in role_mapping.items():
            if v["name"] == r_name:
                return v
        raise RoleException("unknown role name \"%s\"" % r_name)

    def __eq__(self, other):
        if isinstance(other, int):
            return self.rid == other
        elif isinstance(other, str):
            return self.name == other.upper()

    def to_json(self):
        return {
            "rid": self.rid,
            "name": self.name,
            "info": self.info
        }


class RolesType(JSONType):
    impl = sqlalchemy.UnicodeText

    def process_bind_param(self, value, dialect):
        if not isinstance(value, list):
            raise RoleException("unrealizable number")

        roles = []
        for role in value:
            if not isinstance(role, Role):
                raise RoleException("unrealizable number")
            roles.append(role.rid)

        if dialect.name == 'postgresql' and has_postgres_json:
            return roles
        if roles is not None:
            roles = six.text_type(json.dumps(roles))
        return roles

    def process_result_value(self, value, dialect):
        if dialect.name == 'postgresql':
            return [Role(v) for v in value]
        if value is not None:
            value = json.loads(value)
            return [Role(v) for v in value]
        if not isinstance(value, list):
            raise RoleException("unserializable number")
        return value


default_anon_roles = [Role("RESOURCE_VIEW"), Role("USER_CREATE")]
default_registered_roles = [
    Role("USER_REGISTERED"),
    Role("RESOURCE_VIEW"),
    Role("RESOURCE_CREATE"),
    Role("USER_CREATE")
]


def check_role(requirements, **kwargs):
    """Raises exception on bad role"""
    from findex_gui.controllers.user.user import UserController
    if "skip_authorization" in kwargs:
        return

    def check_requirements(user):
        for requirement in requirements:
            roles = [r.name for r in user.roles]
            if requirement not in roles:
                raise RoleException("current user does not have the required role \"%s\"" % requirement)

    try:
        user = UserController.get_current_user(apply_timeout=False)
    except RuntimeError:
        return

    if user:
        if user.admin:
            return
        return check_requirements(user)


def role_req(*requirements):
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            check_role(requirements, **kwargs)
            return f(*args, **kwargs)
        return wrapped_f
    return wrap
