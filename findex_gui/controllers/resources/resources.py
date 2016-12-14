from findex_gui import db, locales, auth
from findex_gui.orm.models import User, UserGroup, Resource, ResourceMeta, ResourceGroup, Server
from findex_common.exceptions import DatabaseException, FindexException
from findex_common.utils import is_ipv4, resolve_hostname


class ResourceController:
    def __init__(self):
        pass

    @staticmethod
    def add_resource(resource_port, resource_protocol, server_name=None, server_address=None, server_id=None,
                     description="", display_url="/", basepath="", recursive_sizes=True,
                     auth_user=None, auth_pass=None, auth_type=None):
        """
        Adds a local or remote file resource.
        :param server_name: Server name
        :param server_address: ipv4 'str'
        :param server_id: server DB id
        :param resource_port: valid port number
        :param resource_protocol: valid protocol number 'int' - see `findex_common.static_variables.FileProtocols`
        :param description: resource description 'str'
        :param display_url: url prefix as it will be shown on the front-end 'str'
        :param basepath: the absolute crawl root path 'str'
        :param recursive_sizes: recursively calculate directory sizes (performance impact during crawl)
        :param auth_user: resource user authentication 'str'
        :param auth_pass: resource pass authentication 'str'
        :param auth_type: resource type authentication 'str'
        :return: resource
        """
        session = db.session()
        if server_id:
            _server = db.session().query(Server).filter(Server.id == server_id).first()
        elif server_name and server_address:
            _server = db.session().query(Server).filter(
                Server.address == server_address,
                Server.name == server_name
            ).first()
        else:
            raise FindexException("Either use server_id to refer to an existing Server "
                                  "object or supply a valid `server_name`, `server_port` "
                                  "and `server_address` parameters.")
        if not _server:
            if not isinstance(server_name, (str, unicode)) or not \
                    isinstance(server_address, (str, unicode)) or not \
                    isinstance(resource_port, int) or not isinstance(resource_protocol, int):
                raise FindexException("Could not auto-add server for resource - requires "
                                      "`server_name`, `server_port`, `server_address`")
            if resource_port > 65535 or resource_port < 1:
                raise FindexException("invalid port")
            _server = ResourceController.add_server(name=server_name,
                                                    hostname=server_address)
        if _server.parents:
            for parent in _server.parents:
                if parent.port == resource_port and parent.protocol == resource_protocol \
                        and parent.basepath == basepath:
                    raise FindexException("Duplicate resource previously defined with id: %d" % parent.id)

        resource = Resource(server=_server,
                            protocol=resource_protocol,
                            port=resource_port,
                            display_url=display_url,
                            basepath=basepath)
        resource.description = description

        rm = ResourceMeta()
        if auth_user and auth_pass:
            rm.set_auth(auth_user, auth_pass, auth_type)
        rm.recursive_sizes = recursive_sizes

        resource.meta = rm
        session.add(resource)
        session.commit()

    @staticmethod
    def add_server(name, ipv4_address=None, hostname=None, verify_hostname=True,
                   use_resolved_hostname=False, description=""):
        """
        :param name:
        :param ipv4_address:
        :param hostname:
        :param description:
        :return:
        """
        if not isinstance(name, (str, unicode)):
            raise FindexException("invalid parameters")
        if not ipv4_address and not hostname:
            raise FindexException("address and hostname cant both be empty")

        _address = None
        session = db.session()
        if ipv4_address:
            if not is_ipv4(ipv4_address):
                raise FindexException("invalid ipv4_address")
            _address = ipv4_address

        if hostname:
            if verify_hostname:
                addr = resolve_hostname(hostname)
                if not addr:
                    raise FindexException("invalid hostname")

                if use_resolved_hostname:
                    hostname = addr
            _address = hostname

        srv = Server()
        srv.address = _address
        srv.name = name
        srv.description = description

        session.add(srv)
        session.commit()

        return srv

    @staticmethod
    def add_resource_group(name, removable=True, description=None):
        session = db.session()
        rg = ResourceGroup(name=name,
                           removable=removable,
                           description=description)
        session.add(rg)
        session.commit()
