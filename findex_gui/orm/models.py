import re
import uuid
from datetime import datetime
from flask import request

from sqlalchemy_zdb import ZdbColumn
from sqlalchemy_zdb.types import FULLTEXT
from sqlalchemy_utils import JSONType, IPAddressType, force_auto_coercion

from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Boolean, DateTime, BigInteger, Index, TIMESTAMP, ForeignKey, Table, Column
)

from flaskext.auth import AuthUser, get_current_user_data

from findex_gui import locales, app
from findex_gui.controllers.user.roles import RolesType
from findex_common.static_variables import ResourceStatus, FileProtocols
from findex_common.utils import Sanitize, rand_str
from findex_common.utils_time import TimeMagic
from findex_common import static_variables

base = declarative_base(name="Model")
force_auto_coercion()


class _extend(object):
    def get(self, column, default=None):
        if hasattr(self, column):
            val = getattr(self, column)
            if val:
                return val
        return default

    @classmethod
    def get_columns(cls, zombodb_only=False):
        """
        Returns the columns for a given sqlalchemy model
        :param zombodb_only: only return columns marked for zombodb
        :return: list of columns
        """
        columns = list(cls.__table__.columns)
        if zombodb_only:
            columns = [column for column in columns if column.info.get('zombodb')]
        return columns

    @classmethod
    def get_columns_as_ddl(cls, zombodb_only=False):
        """
        Returns the column(s) DDL for a given sqlalchemy model
        :param zombodb_only: only return columns marked for zombodb
        :return:
        """
        return ",\n\t".join(
            ["%s %s" % (column.name,
                        column.type) for column in cls.get_columns(zombodb_only=zombodb_only)])


class Server(base, _extend):
    __tablename__ = "server"

    id = Column(Integer, primary_key=True)
    address = Column(String(128), unique=True, nullable=True)

    name = Column(String(64), unique=True, nullable=False)
    description = Column(String(4096), nullable=True)

    parents = relationship("Resource", back_populates="server")

    ix_address = Index("ix_resource_address", address)
    ix_name = Index("ix_resource_name", name)

    def __init__(self, address):
        self.name = uuid.uuid1().hex
        self.address = address

    def set_valid_name(self, name):
        name = re.sub("[^a-zA-Z0-9_\.]", "", name)
        self.name = name

    def to_json(self):
        return {
            "name": self.name,
            "address": self.address,
            "description": self.description
        }


class Resource(base, _extend):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True)

    server_id = Column(Integer, ForeignKey("server.id"), nullable=False)
    server = relationship("Server", back_populates="parents")

    meta_id = Column(Integer, ForeignKey("resource_meta.id"), nullable=False)
    meta = relationship("ResourceMeta", single_parent=True, cascade="all, delete-orphan", backref=backref("resources", uselist=False))

    group_id = Column(Integer, ForeignKey("resource_group.id"))
    group = relationship("ResourceGroup", back_populates="parents")

    created_by_id = Column(Integer, ForeignKey('users.id'))
    created_by = relationship("User")

    description = Column(String(), nullable=True)

    port = Column(Integer(), nullable=False)
    protocol = Column(Integer(), nullable=False)

    display_url = Column(String(), nullable=False)

    date_added = Column(DateTime(), default=datetime.utcnow)
    date_crawl_start = Column(DateTime())
    date_crawl_end = Column(DateTime())

    basepath = Column(String(), nullable=True, default="")

    def __init__(self, server, protocol, port, display_url, basepath):
        self.server = server
        self.port = port
        self.display_url = display_url
        self.protocol = protocol
        self.basepath = basepath

    def to_json(self):
        # @TODO: once  here, once in the resourcecontroller.. no need for duplicate code
        tm = TimeMagic()
        fp = static_variables.FileProtocols()
        rs = static_variables.ResourceStatus()

        out = {
            "server": self.server.to_json(),
            "meta": self.meta.to_json(),
            "group": self.group.to_json(),
            "ago": tm.ago_dt(self.date_crawl_end),
            "status_human": rs.name_by_id(self.meta.status),
            "protocol_human": fp.name_by_id(self.protocol)
        }

        for k, v in self.__dict__.items():
            if not k.startswith("_"):
                if not issubclass(v.__class__, base):
                    out[k] = v

        return out

    @staticmethod
    def make_valid_resourcename(resourcename):
        return re.sub("[^a-zA-Z0-9_\.]", "", resourcename)


class ResourceMeta(base, _extend):
    __tablename__ = "resource_meta"

    id = Column(Integer, primary_key=True)
    file_count = Column(Integer(), nullable=False, default=0)
    status = Column(Integer, nullable=False, default=0)

    auth_user = Column(String, nullable=True)
    auth_pass = Column(String, nullable=True)
    auth_type = Column(String, nullable=True)

    web_user_agent = Column(String, nullable=True)

    relay_user_agent = Column(String, nullable=True)
    relay_proxy = Column(String, nullable=True)
    relay_enabled = Column(Boolean, default=False, nullable=False)

    recursive_sizes = Column(Boolean, nullable=False, default=False)
    file_distribution = Column(JSONType, nullable=True)
    throttle_connections = Column(Boolean, nullable=False, default=False)

    def set_auth(self, username, password, auth_type):
        if username and password and not auth_type:
            raise Exception("auth_type may not be empty")

        self.auth_user = username
        self.auth_pass = password
        self.auth_type = auth_type

    @classmethod
    def is_busy(cls):
        return ResourceStatus().name_by_id(cls.busy)

    def to_json(self):
        return {
            "auth_user": "***",
            "auth_pass": "***",
            "file_count": self.file_count,
            "auth_type": self.auth_type,
            "web_user_agent": self.web_user_agent,
            "recrusive_sizes": self.recursive_sizes,
            "file_distribution": self.file_distribution,
            "throttle_connections": self.throttle_connections
        }


class ResourceGroup(base, _extend):
    __tablename__ = "resource_group"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    added = Column(DateTime(), default=datetime.utcnow, nullable=False)
    removable = Column(Boolean, nullable=False, default=True)

    parents = relationship("Resource", back_populates="group")
    #tasks = relationship("Task", back_populates="group")

    def __init__(self, name, description, removable=True):
        self.name = self.make_valid_groupname(name)
        self.removable = removable
        self.description = description

    @staticmethod
    def make_valid_groupname(groupname):
        groupname = re.sub("[^a-zA-Z0-9_\.]", "", groupname)
        if not groupname:
            raise Exception("group name cannot be empty or invalid")
        return groupname

    def to_json(self):
        out = {
            "name": self.name,
            "description": self.description,
            "added": self.added,
            "removable": self.removable
        }

        return out


task_crawlers = Table(
    '_task_crawlers',
    base.metadata,
    Column('task_id', Integer(), ForeignKey('tasks.id')),
    Column('id', Integer(), ForeignKey('crawlers.id'))
)

task_groups = Table(
    '_task_groups',
    base.metadata,
    Column('task_id', Integer(), ForeignKey('tasks.id')),
    Column('id', Integer(), ForeignKey('resource_group.id'))
)


class Task(base, _extend):
    __tablename__ = "tasks"

    id = Column(Integer(), primary_key=True)

    name = Column(String(), nullable=False, unique=True)
    added = Column(DateTime(), default=datetime.utcnow, nullable=False)
    description = Column(String(), nullable=True)
    uid_frontend = Column(String(), nullable=True)  # @TODO change to false?
    owner_id = Column(Integer(), ForeignKey("users.id"))
    options = Column(JSONType())

    crawlers = relationship("Crawler", secondary=task_crawlers)
    groups = relationship("ResourceGroup", secondary=task_groups)

    ix_name = Index("ix_tasks_name", name)
    ix_uid_frontend = Index("ix_tasks_uid_frontend", uid_frontend)

    def __init__(self, name, owner):
        self.name = name
        self.owner_id = owner.id

    def to_json(self):
        out = {
            "name": self.name,
            "added": self.added,
            "description": self.description,
            "owner_id": self.owner_id,
            "group_id": self.group_id
        }
        return out


class Crawler(base, _extend):
    __tablename__ = "crawlers"

    id = Column(Integer, primary_key=True)

    hostname = Column(String(), nullable=False)
    crawler_name = Column(String(), nullable=False, unique=True)
    heartbeat = Column(TIMESTAMP())

    amqp_id = Column(Integer, ForeignKey("amqp.id"), nullable=False)
    amqp = relationship("Amqp", back_populates="crawlers")


class Amqp(base, _extend):
    __tablename__ = "amqp"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    vhost = Column(String, nullable=False)
    queue = Column(String, nullable=False)

    auth_user = Column(String, nullable=False)
    auth_pass = Column(String)

    added = Column(DateTime(), default=datetime.utcnow)
    crawlers = relationship("Crawler", back_populates="amqp")

    def __init__(self, name, host, port, username, password, queue_name, virtual_host):
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = queue_name
        self.virtual_host = virtual_host


class Options(base, _extend):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True)

    key = Column(String())
    val = Column(JSONType())

    def __init__(self, key, val):
        self.key = key
        self.val = val


class Roles(base, _extend):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True)

    name = Column(String())
    description = Column(String())

    def __init__(self, name, description):
        self.name = name
        self.description = description


user_group_admins = Table(
    '_user_group_admins',
    base.metadata,
    Column('group_id', Integer(), ForeignKey('user_groups.group_id')),
    Column('id', Integer(), ForeignKey('users.id', ondelete='CASCADE'))
)

user_group_members = Table(
    '_user_group_members',
    base.metadata,
    Column('group_id', Integer(), ForeignKey('user_groups.group_id')),
    Column('id', Integer(), ForeignKey('users.id', ondelete='CASCADE'))
)

user_group_resources = Table(
    '_user_group_resources',
    base.metadata,
    Column('group_id', Integer(), ForeignKey('user_groups.group_id')),
    Column('id', Integer(), ForeignKey('resources.id', ondelete='CASCADE'))
)


class UserGroup(base, _extend):
    __tablename__ = "user_groups"

    group_id = Column(Integer, primary_key=True)
    group_name = Column(String(), unique=True)

    admins = relationship("User", secondary=user_group_admins)
    members = relationship("User", secondary=user_group_members)
    resources = relationship("Resource", secondary=user_group_resources)

    created = Column(DateTime(), default=datetime.utcnow, nullable=False)
    description = Column(String(), nullable=True)
    password = Column(String(32), nullable=True)
    invite_only = Column(Boolean, default=False, nullable=False)

    def __init__(self, name, owner):
        """
        :param name: group name
        :param owner: the owner (becomes group admin/leader)
        """
        if not isinstance(owner, User):
            raise Exception("creator must be of type db user")

        self.name = name
        self.admins.append(owner)

    @staticmethod
    def make_valid_group(groupname):
        return re.sub("[^a-zA-Z0-9_\.]", "", groupname)


class User(base, AuthUser, _extend):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String(16), unique=True, nullable=False)
    realname = Column(String(128), nullable=True)
    password = Column(String(120), nullable=False)
    salt = Column(String(16), default=rand_str(16))

    created = Column(DateTime(), default=datetime.utcnow, nullable=False)
    modified = Column(DateTime(), default=datetime.utcnow, nullable=False)

    admin = Column(Boolean, default=False, nullable=False)
    removable = Column(Boolean, default=True, nullable=False)
    roles = Column("roles", RolesType, nullable=False)

    locale = Column(String(8), default='en')

    def __init__(self, *args, **kwargs):
        kwargs["username"] = self.make_valid_username(kwargs.get("username"))
        super(User, self).__init__(*args, **kwargs)

        password = kwargs.get("password")
        if password and not self.id:
            if request:
                self.locale = request.accept_languages.best_match(list(locales.keys()))
            else:
                self.locale = "en"
            with app.app_context():
                self.set_and_encrypt_password(password=password, salt=rand_str(16))

    def __getstate__(self):
        """used by flask.auth lib"""
        return {
            "id": self.id,
            "username": self.username,
            "created": self.created,
            "modified": self.modified,
            "locale": self.locale,
            "admin": self.is_admin(),
            "roles": self.roles
        }

    def taint(self):
        """Should be called to ensure Python dictionaries
        that do not propagate changes, are committed correctly
        by SQLAlchemy upon flush."""
        flag_modified(self, "roles")

    def is_admin(self):
        return True if self.role == 0 and isinstance(self.role, int) else False

    @staticmethod
    def make_valid_username(username):
        return re.sub("[^a-zA-Z0-9_\.]", "", username)

    @classmethod
    def load_current_user(cls, apply_timeout=True):
        data = get_current_user_data(apply_timeout)
        if not data:
            return None

        return cls.query.filter(cls.username == data["username"]).one()


class Files(base, _extend):
    __tablename__ = "files"

    id = Column(BigInteger, primary_key=True)

    resource_id = ZdbColumn(Integer())

    file_name = Column(String())
    file_path = Column(String())
    file_ext = ZdbColumn(String(8))
    file_format = ZdbColumn(Integer())
    file_isdir = ZdbColumn(Boolean())
    file_size = ZdbColumn(BigInteger())

    file_modified = Column(DateTime())

    file_perm = Column(Integer())

    searchable = ZdbColumn(FULLTEXT(41))

    ix_resource_id = Index("ix_resource_id", resource_id)
    ix_host_id_file_path = Index("ix_resource_id_file_path", resource_id, file_path)

    # CREATE INDEX ix_file_searchable_gin ON files USING gin(searchable gin_trgm_ops);
    # ix_file_searchable_gin = Index("ix_file_searchable_gin", searchable, postgresql_using="gin", postgresql_ops={
    #     "searchable": "gin_trgm_ops"
    # })

    def fancify(self):
        # @TODO: remove this shit
        from findex_common.static_variables import FileProtocols, FileCategories
        obj = Sanitize(self).humanize(humandates=True, humansizes=True,  dateformat="%d %b %Y")

        file_url = "%s%s" % (obj.file_path, obj.file_name)
        display_url = obj.resource.display_url
        if display_url.endswith("/"):
            display_url = display_url[:-1]

        setattr(obj, "path_dir", "%s:%d%s" % (
            obj.resource.server.address,
            obj.resource.port,
            obj.file_path))
        setattr(obj, "path_file", "%s:%d%s%s%s" % (
            obj.resource.server.address,
            obj.resource.port,
            obj.file_path,
            obj.file_name,
            "/" if obj.file_isdir else ""))
        setattr(obj, "file_format_human", FileCategories().name_by_id(obj.file_format))
        if display_url:
            setattr(obj, "path_direct", display_url + file_url)
        else:
            setattr(obj, "path_direct", "%s://%s:%s%s%s" % (FileProtocols().name_by_id(
                obj.resource.protocol), obj.resource.server.address, obj.resource.port, obj.resource.basepath, file_url))

        return obj

    def to_json(self):
        blob = {k: v for k, v in self.__dict__.items() if not k.startswith("_") and not issubclass(v.__class__, base)}

        blob["resource"] = {
            "address": self.resource.server.address
        }

        return blob