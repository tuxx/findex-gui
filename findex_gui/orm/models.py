import re
import uuid
from datetime import datetime

from flask import request
import humanfriendly
import sqlalchemy_zdb
from findex_gui.bin.config import config
sqlalchemy_zdb.ES_HOST = config("findex:elasticsearch:host")
from sqlalchemy_zdb import ZdbColumn
from sqlalchemy_zdb.types import FULLTEXT

from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import (
    Integer, String, Boolean, DateTime, BigInteger, Index, TIMESTAMP,
    ForeignKey, Table, Column, SMALLINT, ARRAY
)
from sqlalchemy_utils import IPAddressType, force_auto_coercion
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_json import MutableJson

from findex_common.static_variables import ResourceStatus, FileProtocols, FileCategories
from findex_common.crawl import make_resource_search_column
from findex_common.utils import random_str
from findex_common.utils_time import TimeMagic
from findex_common import static_variables
from findex_gui.bin.utils import Extended
from findex_gui.controllers.auth.auth import AuthUser, get_current_user_data
from findex_gui.controllers.user.roles import RolesType

BASE = declarative_base(name="Model")
force_auto_coercion()


class Server(BASE, Extended):
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


class Resource(BASE, Extended):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True)

    server_id = Column(Integer, ForeignKey("server.id"), nullable=False)
    server = relationship("Server", back_populates="parents")

    meta_id = Column(Integer, ForeignKey("resource_meta.id"), nullable=False)
    meta = relationship("ResourceMeta", single_parent=True, cascade="all, delete-orphan", backref=backref("resources", uselist=False))

    group_id = Column(Integer, ForeignKey("resource_group.id"))
    group = relationship("ResourceGroup", back_populates="parents")

    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_by = relationship("User")

    description = Column(String(), nullable=True)

    port = Column(Integer(), nullable=False)
    protocol = Column(Integer(), nullable=False)

    display_url = Column(String(), nullable=False)

    date_added = Column(DateTime(), default=datetime.utcnow)
    date_crawl_start = Column(DateTime())
    date_crawl_end = Column(DateTime())

    # this search column will be used for front-end
    # searching capabilities, it will include:
    # "SERVER_ADDRESS, SERVER_NAME, DISPLAY_URL, PROTOCOL(str)"
    search = ZdbColumn(FULLTEXT(), nullable=False)

    basepath = Column(String(), nullable=True, default="")

    def __init__(self, server, protocol, port, display_url, basepath):
        self.server = server
        self.port = port
        self.display_url = display_url
        self.protocol = protocol
        self.basepath = basepath
        self.search = make_resource_search_column(server_address=server.address,
                                                  server_name=server.name,
                                                  display_url=display_url,
                                                  resource_port=port)

    @property
    def protocol_human(self):
        protocol = static_variables.FileProtocols()
        return protocol.name_by_id(self.protocol)

    @property
    def date_added_ago(self):
        return TimeMagic().ago_dt(self.date_added)

    @property
    def date_crawl_end_ago(self):
        return TimeMagic().ago_dt(self.date_crawl_end)

    @property
    def status_human(self):
        status = static_variables.ResourceStatus()
        return status.name_by_id(self.meta.status)

    @property
    def resource_id(self):
        return "%s:%d" % (self.server.address, self.port)

    @staticmethod
    def make_valid_resourcename(resourcename):
        return re.sub("[^a-zA-Z0-9_\.]", "", resourcename)


class ResourceMeta(BASE, Extended):
    __tablename__ = "resource_meta"

    id = Column(Integer, primary_key=True)
    file_count = Column(Integer(), nullable=False, default=0)
    status = Column(Integer, nullable=False, default=0)

    auth_user = Column(String, nullable=True, info={"exclude_json": True})
    auth_pass = Column(String, nullable=True, info={"exclude_json": True})
    auth_type = Column(String, nullable=True)

    web_user_agent = Column(String, nullable=True)

    relay_user_agent = Column(String, nullable=True)
    relay_proxy = Column(String, nullable=True)
    relay_enabled = Column(Boolean, default=False, nullable=False)

    recursive_sizes = Column(Boolean, nullable=False, default=False)
    file_distribution = Column(MutableJson, nullable=True)
    throttle_connections = Column(Boolean, nullable=False, default=False)

    banner = Column(String(), nullable=True)
    response_time = Column(Integer(), nullable=True)
    uid = Column(String(), nullable=True)

    def set_auth(self, username, password, auth_type):
        if username and password and not auth_type:
            raise Exception("auth_type may not be empty")

        self.auth_user = username
        self.auth_pass = password
        self.auth_type = auth_type

    @classmethod
    def is_busy(cls):
        return ResourceStatus().name_by_id(cls.busy)


class ResourceGroup(BASE, Extended):
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


task_crawlers = Table(
    "_task_crawlers",
    BASE.metadata,
    Column("task_id", Integer(), ForeignKey("tasks.id")),
    Column("id", Integer(), ForeignKey("crawlers.id"))
)

task_groups = Table(
    "_task_groups",
    BASE.metadata,
    Column("task_id", Integer(), ForeignKey("tasks.id")),
    Column("id", Integer(), ForeignKey("resource_group.id"))
)


class Task(BASE, Extended):
    __tablename__ = "tasks"

    id = Column(Integer(), primary_key=True)

    name = Column(String(), nullable=False, unique=True)
    added = Column(DateTime(), default=datetime.utcnow, nullable=False)
    description = Column(String(), nullable=True)
    uid_frontend = Column(String(), nullable=True)  # @TODO change to false?
    owner_id = Column(Integer(), ForeignKey("users.id"))
    options = Column(MutableJson())

    crawlers = relationship("Crawler", secondary=task_crawlers)
    groups = relationship("ResourceGroup", secondary=task_groups)

    ix_name = Index("ix_tasks_name", name)
    ix_uid_frontend = Index("ix_tasks_uid_frontend", uid_frontend)

    def __init__(self, name, owner):
        self.name = name
        self.owner_id = owner.id


class Crawler(BASE, Extended):
    __tablename__ = "crawlers"

    id = Column(Integer, primary_key=True)

    hostname = Column(String(), nullable=False)
    crawler_name = Column(String(), nullable=False, unique=True)
    heartbeat = Column(TIMESTAMP())

    amqp_id = Column(Integer, ForeignKey("amqp.id"), nullable=False)
    amqp = relationship("Amqp", back_populates="crawlers")


class Amqp(BASE, Extended):
    __tablename__ = "amqp"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    vhost = Column(String, nullable=False)
    queue = Column(String, nullable=False)

    auth_user = Column(String, nullable=False, info={"exclude_json": True})
    auth_pass = Column(String, info={"exclude_json": True})

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


class Options(BASE, Extended):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True)

    key = Column(String())
    val = Column(MutableJson())

    def __init__(self, key, val):
        self.key = key
        self.val = val


class Roles(BASE, Extended):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True)

    name = Column(String())
    description = Column(String())

    def __init__(self, name, description):
        self.name = name
        self.description = description


user_group_admins = Table(
    "_user_group_admins",
    BASE.metadata,
    Column("group_id", Integer(), ForeignKey("user_groups.group_id")),
    Column("id", Integer(), ForeignKey("users.id", ondelete="CASCADE"))
)

user_group_members = Table(
    "_user_group_members",
    BASE.metadata,
    Column("group_id", Integer(), ForeignKey("user_groups.group_id")),
    Column("id", Integer(), ForeignKey("users.id", ondelete="CASCADE"))
)

user_group_resources = Table(
    "_user_group_resources",
    BASE.metadata,
    Column("group_id", Integer(), ForeignKey("user_groups.group_id")),
    Column("id", Integer(), ForeignKey("resources.id", ondelete="CASCADE"))
)


class UserGroup(BASE, Extended):
    __tablename__ = "user_groups"

    group_id = Column(Integer, primary_key=True)
    group_name = Column(String(), unique=True)

    admins = relationship("User", secondary=user_group_admins)
    members = relationship("User", secondary=user_group_members)
    resources = relationship("Resource", secondary=user_group_resources)

    created = Column(DateTime(), default=datetime.utcnow, nullable=False)
    description = Column(String(), nullable=True)
    password = Column(String(32), nullable=True, info={"json_exclude": True})
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


class User(BASE, AuthUser, Extended):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String(16), unique=True, nullable=False)
    realname = Column(String(128), nullable=True, info={"json_exclude": True})
    password = Column(String(120), nullable=False, info={"json_exclude": True})
    salt = Column(String(32), default=random_str(16), info={"json_exclude": True})

    created = Column(DateTime(), default=datetime.utcnow, nullable=False)
    modified = Column(DateTime(), default=datetime.utcnow, nullable=False)

    admin = Column(Boolean, default=False, nullable=False)
    removable = Column(Boolean, default=True, nullable=False)
    roles = Column("roles", RolesType, nullable=False)

    locale = Column(String(8), default="en")

    def __init__(self, *args, **kwargs):
        from findex_gui.web import locales, app
        kwargs["username"] = self.make_valid_username(kwargs.get("username"))
        super(User, self).__init__(*args, **kwargs)

        password = kwargs.get("password")
        if password and not self.id:
            if request:
                self.locale = request.accept_languages.best_match(list(locales.keys()))
            else:
                self.locale = "en"
            with app.app_context():
                self.set_and_encrypt_password(password=password, salt=random_str(16))

    def __getstate__(self):
        """used by flask.auth lib"""
        return {
            "id": self.id,
            "username": self.username,
            "created": self.created,
            "modified": self.modified,
            "locale": self.locale,
            "admin": self.admin,
            "roles": self.roles
        }

    def taint(self):
        """Should be called to ensure Python dictionaries
        that do not propagate changes, are committed correctly
        by SQLAlchemy upon flush."""
        flag_modified(self, "roles")

    @staticmethod
    def make_valid_username(username):
        return re.sub("[^a-zA-Z0-9_\.]", "", username)

    @classmethod
    def load_current_user(cls, apply_timeout=True):
        data = get_current_user_data(apply_timeout)
        if not data:
            return None

        return cls.query.filter(cls.username == data["username"]).one()


class MetaImdb(BASE, Extended):
    __tablename__ = "meta_imdb"

    id = Column(SMALLINT, primary_key=True)

    title = ZdbColumn(FULLTEXT(), nullable=False)
    year = ZdbColumn(SMALLINT(), nullable=False)
    rating = ZdbColumn(SMALLINT(), nullable=False)
    director = ZdbColumn(FULLTEXT())
    genres = ZdbColumn(ARRAY(String(32)))
    actors = ZdbColumn(ARRAY(String(64)))
    plot = ZdbColumn(String())


class MetaImdbActors(BASE, Extended):
    __tablename__ = "meta_imdb_actors"

    id = Column(SMALLINT, primary_key=True)
    actor = ZdbColumn(FULLTEXT())


class MetaImdbDirectors(BASE, Extended):
    __tablename__ = "meta_imdb_directors"

    id = Column(SMALLINT, primary_key=True)
    director = ZdbColumn(FULLTEXT())


class Post(BASE, Extended):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)

    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_by = relationship("User")

    title = Column(String(), nullable=False)
    content = Column(String(), nullable=False)
    date_added = Column(DateTime(), default=datetime.utcnow, nullable=False)

    def __init__(self, created_by, content, title):
        self.created_by = created_by
        self.content = content
        self.title = title

    @property
    def ago(self):
        return TimeMagic().ago_dt(self.date_added)


class Files(BASE, Extended):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)

    resource_id = ZdbColumn(Integer())

    file_name = Column(String())
    file_path = Column(String())
    file_ext = ZdbColumn(String(8))
    file_format = ZdbColumn(Integer())
    file_isdir = ZdbColumn(Boolean())
    file_size = ZdbColumn(BigInteger())

    file_modified = Column(DateTime())

    file_perm = Column(SMALLINT())

    searchable = ZdbColumn(FULLTEXT(41))

    meta_info = ZdbColumn(MutableJson())
    meta_imdb_id = ZdbColumn(SMALLINT())
    meta_imdb = None
    # meta_imdb_id = ZdbColumn(ForeignKey(MetaImdb.id))
    # meta_imdb = relationship(MetaImdb)

    ix_resource_id = Index("ix_resource_id", resource_id)
    ix_host_id_file_path = Index("ix_resource_id_file_path", resource_id, file_path)

    # CREATE INDEX ix_file_searchable_gin ON files USING gin(searchable gin_trgm_ops);
    # ix_file_searchable_gin = Index("ix_file_searchable_gin", searchable, postgresql_using="gin", postgresql_ops={
    #     "searchable": "gin_trgm_ops"
    # })

    def get_json(self, depth=0):
        json = super(BASE, self).get_json()
        json["resource"] = {
            "address": self.resource.server.address
        }
        return json

    def get_meta_imdb(self):
        if self.meta_imdb_id is None:
            return
        from findex_gui.web import db
        self.meta_imdb = db.session.query(MetaImdb).filter(MetaImdb.id == self.meta_imdb_id).first()
        return self.meta_imdb

    @property
    def file_name_human(self):
        return "%s%s%s" % (self.file_name,
                           "." if not self.file_isdir else "",
                           self.file_ext)

    @property
    def file_modified_human(self):
        return self.file_modified.strftime("%d %b %Y")

    @property
    def file_format_human(self):
        return FileCategories().name_by_id(self.file_format)

    @property
    def file_size_human(self):
        return humanfriendly.format_size(self.file_size)

    @property
    def path_dir(self):
        return "%s:%d%s" % (
            self.resource.server.address,
            self.resource.port,
            self.file_path)

    @property
    def path_file(self):
        return "%s:%d%s%s%s" % (
            self.resource.server.address,
            self.resource.port,
            self.file_path,
            self.file_name_human,
            "/" if self.file_isdir else "")

    @property
    def path_direct(self):
        display_url = self.resource.display_url
        if display_url.endswith("/"):
            display_url = display_url[:-1]

        if display_url:
            return display_url + self.file_url
        else:
            return "%s://%s:%s%s%s" % (
                FileProtocols().name_by_id(self.resource.protocol),
                self.resource.server.address,
                self.resource.port,
                self.resource.basepath,
                self.file_url)

    @property
    def file_url(self):
        return "%s%s" % (self.file_path, self.file_name_human)


class NmapRule(BASE, Extended):
    __tablename__ = "nmap_rules"

    id = Column(SMALLINT, primary_key=True)
    rule = Column(String(), nullable=False, unique=True)
    date_added = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, rule):
        self.rule = rule
