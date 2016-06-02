import re
from json import loads
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, BigInteger, Index, TIMESTAMP, ForeignKey, Sequence
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import JSONType, IPAddressType
from sqlalchemy.ext.declarative import declarative_base
from flaskext.auth import AuthUser, get_current_user_data

from findex_common.static_variables import ResourceStatus
from findex_common.utils import Sanitize

base = declarative_base(name='Model')
from sqlalchemy_utils import force_auto_coercion

force_auto_coercion()


class Users(base, AuthUser):
    __tablename__ = 'user'  # @TODO: change to users

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    salt = Column(String(80))
    role = Column(Integer, default=1)
    created = Column(DateTime(), default=datetime.utcnow)
    modified = Column(DateTime())

    group_id = Column(Integer, ForeignKey('user_group.id'))
    group = relationship("UserGroup", back_populates="users")

    locale = Column(String(8), default='en')

    def __init__(self, *args, **kwargs):
        kwargs['username'] = self.make_valid_username(kwargs.get('username'))
        super(Users, self).__init__(*args, **kwargs)

        # Initialize and encrypt password before first save.
        password = kwargs.get('password')
        if password is not None and not self.id:
            self.created = datetime.utcnow()
            self.set_and_encrypt_password(password)

    def __getstate__(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'created': self.created,
            'modified': self.modified,
            'locale': self.locale,
            'admin': self.is_admin()
        }

    @classmethod
    def is_admin(cls):
        return True if cls.role == 0 and isinstance(cls.role, int) else False

    @staticmethod
    def make_valid_username(username):
        return re.sub('[^a-zA-Z0-9_\.]', '', username)

    @classmethod
    def load_current_user(cls, apply_timeout=True):
        data = get_current_user_data(apply_timeout)
        if not data:
            return None

        return cls.query.filter(cls.username == data['username']).one()


class UserGroup(base):
    __tablename__ = 'user_group'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)
    description = Column(String)

    added = Column(DateTime(), default=datetime.utcnow)

    users = relationship("Users", back_populates="group")

    def __init__(self, name, description):
        self.name = name
        self.description = description

    @staticmethod
    def make_valid_group(groupname):
        return re.sub('[^a-zA-Z0-9_\.]', '', groupname)


class Files(base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)

    resource_id = Column(Integer())

    file_name = Column(String())
    file_path = Column(String())
    file_ext = Column(String(8))
    file_format = Column(Integer())
    file_isdir = Column(Boolean())
    file_size = Column(BigInteger())

    file_modified = Column(DateTime())

    file_perm = Column(Integer())

    searchable = Column(String(23))

    # regular indexes
    ix_file_ext = Index('ix_file_ext', file_ext)
    ix_file_size = Index('ix_file_size', file_size)

    # multi column indexes
    ix_host_id_file_path = Index('ix_resource_id_file_path', resource_id, file_path)
    ix_file_format_searchable = Index('ix_file_format_searchable', file_format, searchable)

    # @TODO: support more than postgres type indexes
    # full text search LIKE '%needle%'
    ix_file_searchable_gin = Index('ix_file_searchable_gin', searchable, postgresql_using='gin', postgresql_ops={
        'searchable': 'gin_trgm_ops'
    })

    def fancify(self):
        obj = Sanitize(self).humanize(humandates=True, humansizes=True,  dateformat="%d %b %Y")

        file_url = '%s%s' % (obj.file_path, obj.file_name)
        display_url = obj.resource.display_url
        if display_url.endswith('/'):
            display_url = display_url[:-1]

        setattr(obj, 'path_dir', '/browse/%s%s' % (obj.resource.name, obj.file_path))
        setattr(obj, 'path_file', '/browse/%s%s%s%s' % (obj.resource.name, obj.file_path, obj.file_name, '/' if obj.file_isdir else ''))
        setattr(obj, 'path_direct', display_url + file_url)

        return obj

    def make_dict(self):
        blob = {k: v for k, v in self.__dict__.iteritems() if not k.startswith('_') and not issubclass(v.__class__, base)}

        blob['resource'] = {
            'address': self.resource.address
        }

        return blob


class Crawlers(base):
    __tablename__ = 'crawlers'

    id = Column(Integer, primary_key=True)
    hostname = Column(String(), nullable=False)
    crawler_name = Column(String(), nullable=False, unique=True)

    amqp_host = Column(String(128))
    amqp_vhost = Column(String(128))
    heartbeat = Column(TIMESTAMP())


class Resources(base):
    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True)

    name = Column(String(), unique=True, nullable=False)
    description = Column(String(), default='')

    address = Column(String(), nullable=False)
    port = Column(Integer(), nullable=False, default=0)
    protocol = Column(Integer(), nullable=False)

    display_url = Column(String(), nullable=False)

    date_added = Column(DateTime(), default=datetime.utcnow)
    date_crawl_start = Column(DateTime())
    date_crawl_end = Column(DateTime())

    basepath = Column(String(), nullable=True, default='')

    meta_id = Column(Integer, ForeignKey('resource_meta.id'))
    meta = relationship("ResourceMeta", single_parent=True, cascade="all, delete-orphan", backref=backref("resources", uselist=False))

    group_id = Column(Integer, ForeignKey('resource_group.id'))
    group = relationship("ResourceGroup", back_populates="parents")

    ix_address = Index('ix_resource_address', address)
    ix_name = Index('ix_resource_name', name)

    def __init__(self, name, address, port, display_url, basepath, protocol):
        self.name = name
        self.address = address
        self.port = port
        self.display_url = display_url
        self.protocol = protocol
        self.basepath = basepath

    def make_dict(self):
        blob = {k: v for k, v in self.__dict__.iteritems() if not k.startswith('_') and not issubclass(v.__class__, base)}
        return blob

    @staticmethod
    def make_valid_resourcename(resourcename):
        return re.sub('[^a-zA-Z0-9_\.]', '', resourcename)


class ResourceMeta(base):
    __tablename__ = 'resource_meta'

    id = Column(Integer, primary_key=True)
    file_count = Column(Integer(), nullable=True, default=0)
    busy = Column(Integer, nullable=True, default=False)

    auth_user = Column(String)
    auth_pass = Column(String)

    web_user_agent = Column(String)

    recursive_sizes = Column(Boolean, nullable=False, default=False)
    file_distribution = Column(JSONType)

    @classmethod
    def is_busy(cls):
        return ResourceStatus().name_by_id(cls.busy)


class Amqp(base):
    __tablename__ = 'amqp'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    vhost = Column(String, nullable=False)
    queue = Column(String, nullable=False)

    auth_user = Column(String, nullable=False)
    auth_pass = Column(String)

    added = Column(DateTime(), default=datetime.utcnow)

    parents = relationship("ResourceGroup", back_populates="amqp")

    def __init__(self, name, host, port, username, password, queue_name, virtual_host):
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = queue_name
        self.virtual_host = virtual_host


class Tasks(base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)
    added = Column(DateTime(), default=datetime.utcnow)
    description = Column(String, nullable=False)
    uid_frontend = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey('user.id'))
    data = Column(String, nullable=False)
    groups = relationship('ResourceGroup', backref="group", cascade="all", lazy='dynamic')

    ix_name = Index('ix_tasks_name', name)
    ix_uid_frontend = Index('ix_tasks_uid_frontend', uid_frontend)

    def __init__(self, name, desc, data, owner):
        self.name = name
        self.description = desc
        self.data = data
        self.owner = owner


class ResourceGroup(base):
    __tablename__ = 'resource_group'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)
    description = Column(String)

    added = Column(DateTime(), default=datetime.utcnow)

    parents = relationship("Resources", back_populates="group")

    amqp_id = Column(Integer, ForeignKey('amqp.id'))
    amqp = relationship("Amqp", back_populates="parents")

    task_id = Column(Integer, ForeignKey('tasks.id'))

    def __init__(self, name, host, port, username, password, queue_name, virtual_host):
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = queue_name
        self.virtual_host = virtual_host

    @staticmethod
    def make_valid_groupname(groupname):
        return re.sub('[^a-zA-Z0-9_\.]', '', groupname)


class Options(base):
    __tablename__ = 'options'

    id = Column(Integer, primary_key=True)

    key = Column(String())
    val = Column(JSONType())

    def __init__(self, key, val):
        self.key = key
        self.val = val