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


class User(base, AuthUser):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    salt = Column(String(80))
    role = Column(String(80))
    created = Column(DateTime(), default=datetime.utcnow)
    modified = Column(DateTime())

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        password = kwargs.get('password')

        # Initialize and encrypt password before first save.
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
        }

    @classmethod
    def load_current_user(cls, apply_timeout=True):
        data = get_current_user_data(apply_timeout)
        if not data:
            return None
        return cls.query.filter(cls.username == data['username']).one()


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

    def __init__(self, file_name, file_path, file_ext, file_format, file_isdir, file_modified, file_perm, searchable, file_size, resource_id, img_icon=None):
        self.resource_id = resource_id
        self.file_name = file_name
        self.file_path = file_path
        self.file_ext = file_ext
        self.file_format = file_format
        self.file_size = file_size
        self.file_isdir = file_isdir
        self.file_modified = file_modified
        self.file_perm = file_perm
        self.searchable = searchable
        self.img_icon = None

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
        setattr(obj, 'path_file', '/browse/%s%s%s' % (obj.resource.name, obj.file_path, obj.file_name))
        setattr(obj, 'path_direct', display_url + file_url)

        return obj

    def to_dict(self):
        blob = {k: v for k, v in self.__dict__.iteritems() if not k.startswith('_') and not issubclass(v.__class__, base)}

        blob['resource'] = {
            'address': self.resource.address
        }

        return blob


class Crawlers(base):
    __tablename__ = 'crawlers'

    id = Column(Integer, primary_key=True)
    hostname = Column(String(), nullable=False)
    crawler_name = Column(String(), nullable=False)

    amqp_host = Column(String(128))
    amqp_vhost = Column(String(128))
    heartbeat = Column(TIMESTAMP())


class Resources(base):
    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True)

    name = Column(String(), unique=True, nullable=False)
    description = Column(String())

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

    ix_address = Index('ix_address', address)
    ix_name = Index('ix_name', name)

    def __init__(self, address, display_url, date_crawl_start, date_crawl_end, file_count, protocol, description, hostname):
        self.address = address
        self.hostname = hostname
        self.display_url = display_url
        self.date_crawl_start = date_crawl_start
        self.date_crawl_end = date_crawl_end
        self.file_count = file_count
        self.protocol = protocol
        self.description = description

    def to_dict(self):
        blob = {k: v for k, v in self.__dict__.iteritems() if not k.startswith('_') and not issubclass(v.__class__, base)}
        return blob


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

    name = Column(String, nullable=False)
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

    name = Column(String, nullable=False)
    added = Column(DateTime(), default=datetime.utcnow)
    description = Column(String, nullable=False)
    uid_frontend = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    data = Column(String, nullable=False)
    groups = relationship('ResourceGroup', backref="group", cascade="all", lazy='dynamic')

    ix_name = Index('ix_name', name)
    ix_uid_frontend = Index('ix_uid_frontend', uid_frontend)

    def __init__(self, name, desc, data, owner):
        self.name = name
        self.description = desc
        self.data = data
        self.owner = owner


class ResourceGroup(base):
    __tablename__ = 'resource_group'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
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


class Options(base):
    __tablename__ = 'options'

    id = Column(Integer, primary_key=True)

    key = Column(String())
    val = Column(JSONType())

    def __init__(self, key, val):
        self.key = key
        self.val = val