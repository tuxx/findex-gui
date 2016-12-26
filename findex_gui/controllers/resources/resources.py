from findex_gui import db, locales, auth
from findex_gui.orm.models import User, UserGroup, Resource, ResourceMeta, ResourceGroup, Server
from findex_gui.controllers.user.roles import role_req, check_role
from findex_gui.controllers.user.user import UserController
from findex_common.exceptions import DatabaseException, FindexException
from findex_common.utils import is_ipv4, resolve_hostname
from findex_common import static_variables


class ResourceController:
    @staticmethod
    def get_resources(by_owner=None):
        query = db.session.query(Resource)

        if by_owner:
            query = query.filter(Resource.created_by_id == by_owner)

        all = query.all()
        return all

    @staticmethod
    @role_req("USER_REGISTERED", "RESOURCE_CREATE")
    def add_resource(resource_port, resource_protocol, server_name=None, server_address=None, server_id=None,
                     description="", display_url="/", basepath="", recursive_sizes=True,
                     auth_user=None, auth_pass=None, auth_type=None, web_user_agent=static_variables.user_agent,
                     throttle_connections=False):
        """
        Adds a local or remote file resource
        :param server_name: Server name
        :param server_address: ipv4 'str' - clean hostname or IP
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
        :param web_user_agent: The string to identify ourselves with against the service 'str'
        :param throttle_connections: Wait X seconds between each request/connection 'int'
        :return: resource
        """
        if server_id:
            _server = db.session.query(Server).filter(Server.id == server_id).first()
        elif server_address:
            _server = db.session.query(Server).filter(Server.address == server_address).first()
        else:
            raise FindexException("Either use server_id to refer to an existing Server "
                                  "object or supply a valid `server_name`, `server_port` "
                                  "and/or `server_address` parameters.")
        if not _server:
            if not isinstance(server_address, (str, unicode)) or not \
                    isinstance(resource_port, int) or not isinstance(resource_protocol, int):
                raise FindexException("Could not auto-add server for resource - requires "
                                      "`resource_port`, `resource_protocol` and `server_address`")
            if resource_port > 65535 or resource_port < 1:
                raise FindexException("invalid port")
            _server = ResourceController.add_server(name=server_name,
                                                    hostname=server_address)
        if _server.parents:
            for parent in _server.parents:
                if parent.port == resource_port and parent.protocol == resource_protocol \
                        and parent.basepath == basepath:
                    raise FindexException("Duplicate resource previously defined with resource id: %d" % parent.id)

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
        rm.web_user_agent = web_user_agent
        rm.throttle_connections = throttle_connections
        resource.meta = rm

        current_user = UserController.get_current_user(apply_timeout=False)
        if not current_user:
            raise FindexException("Could not fetch the current user")

        resource.created_by = current_user

        print "yay"
        db.session.add(resource)
        db.session.commit()

        resource.group = db.session.query(ResourceGroup).filter(ResourceGroup.name == "Default").first()
        db.session.commit()

        return True

    @staticmethod
    def add_server(name=None, ipv4_address=None, hostname=None, verify_hostname=True,
                   use_resolved_hostname=False, description=""):
        """
        :param name:
        :param ipv4_address:
        :param hostname:
        :param description:
        :return:
        """
        if not ipv4_address and not hostname:
            raise FindexException("address and hostname cant both be empty")
        _address = None
        if ipv4_address:
            if not is_ipv4(ipv4_address):
                raise FindexException("invalid ipv4_address")
            _address = ipv4_address
        if hostname:
            if verify_hostname:
                addr = resolve_hostname(hostname)
                if use_resolved_hostname:
                    if not addr:
                        raise FindexException("invalid hostname")
                    hostname = addr
            _address = hostname
        srv = Server(_address)
        if name:
            if not isinstance(name, (str, unicode)):
                raise FindexException("invalid parameters")
            srv.set_valid_name(name)
        srv.description = description
        db.session.add(srv)
        db.session.commit()
        return srv

    @staticmethod
    def add_resource_group(name, removable=True, description=None):
        try:
            rg = ResourceGroup(name=name,
                               removable=removable,
                               description=description)
            db.session.add(rg)
            db.session.commit()
            return rg
        except Exception as ex:
            db.session.rollback()
            return DatabaseException(ex)
