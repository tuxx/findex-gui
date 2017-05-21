from findex_gui.web import db, locales, auth
from findex_gui.orm.models import User, UserGroup, Resource, ResourceMeta, ResourceGroup, Server
from findex_gui.controllers.user.roles import role_req, check_role
from findex_gui.controllers.user.user import UserController
from findex_common.exceptions import DatabaseException, FindexException
from findex_common.utils import is_ipv4, resolve_hostname
from findex_common import static_variables
from findex_common.utils_time import TimeMagic


class ResourceController:
    @staticmethod
    @role_req("RESOURCE_VIEW")
    def get_resource(resource_id):
        query = db.session.query(Resource)

        if resource_id:
            query = query.filter(Resource.id == resource_id)

        return query.first()

    @staticmethod
    @role_req("RESOURCE_VIEW")
    def get_resources(uid: int = None, name: str = None, address: str = None,
                      port: int = None, limit: int = None, by_owner: int = None):
        q = db.session.query(Resource)

        if isinstance(by_owner, int):
            q = q.filter(Resource.created_by_id == by_owner)

        if isinstance(uid, int):
            q = q.filter(Resource.id == uid)

        if isinstance(address, str):
            qs = Server.query
            server = qs.filter(Server.address == address).first()
            if not server:
                raise Exception("Could not find server")
            q = q.filter(Resource.server_id == server.id)

        if isinstance(port, int):
            q = q.filter(Resource.port == port)

        if isinstance(name, str):
            qs = Server.query
            server = qs.filter(Server.name == name).first()
            if not server:
                raise Exception("Could not find server")

            q = q.filter(Resource.server_id == server.id)

        if limit and isinstance(limit, int):
            q = q.limit(limit)

        return q.all()

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
            if not isinstance(server_address, str) or not \
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

        if basepath.endswith("/"):
            basepath = basepath[:-1]
        elif not basepath.startswith("/") and len(basepath) > 1:
            basepath = "/%s" % basepath

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

        db.session.add(resource)
        db.session.commit()

        resource.group = db.session.query(ResourceGroup).filter(ResourceGroup.name == "Default").first()
        db.session.commit()
        db.session.flush()

        return True

    @staticmethod
    @role_req("USER_REGISTERED", "RESOURCE_REMOVE", "RESOURCE_CREATE")
    def remove_resource(resource_id, auto_remove_server=True, **kwargs):
        """
        Removes a resource from the database.
        :param resource_id: The resource ID
        :param auto_remove_server: removes the server this resource
        has a relationship with, but only when that server does not
        have any other existing resource members/childs
        :param kwargs:
        :return:
        """
        user = UserController.get_current_user()

        if not user.admin:
            resources = ResourceController.get_resources(by_owner=user.id)
            resource = [r for r in resources if r.id == resource_id]
            if not resource or isinstance(resource, Exception):
                raise FindexException("Could not fetch resource id \"%d\"" % resource_id)
            else:
                resource = resource[0]
        else:
            resource = db.session.query(Resource).filter(Resource.id==resource_id).first()
            if not resource:
                raise FindexException("Could not fetch resource id \"%d\"" % resource_id)

        if auto_remove_server:
            # check for other server resource members before trying to delete
            server = resource.server
            if [z for z in server.parents if z.id != resource_id]:
                # cant remove server, it still has one or more member(s)
                db.session.delete(resource)
            else:
                db.session.delete(resource)
                db.session.delete(server)
        else:
            db.session.delete(resource)

        db.session.commit()
        db.session.flush()

    @staticmethod
    @role_req("USER_REGISTERED", "RESOURCE_CREATE")
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
            if not isinstance(name, str):
                raise FindexException("invalid parameters")
            srv.set_valid_name(name)
        srv.description = description
        db.session.add(srv)
        db.session.commit()
        db.session.flush()
        return srv

    @staticmethod
    @role_req("USER_REGISTERED", "RESOURCE_CREATE")
    def add_resource_group(name, removable=True, description=None, log_error=True, **kwargs):
        try:
            rg = ResourceGroup(name=name,
                               removable=removable,
                               description=description)
            db.session.add(rg)
            db.session.commit()
            db.session.flush()
            return rg
        except Exception as ex:
            db.session.rollback()
            return DatabaseException(ex, log_error)

    @staticmethod
    @role_req("USER_REGISTERED", "RESOURCE_VIEW")
    def get_resource_group(uid=None, name=None):
        query = db.session.query(ResourceGroup)

        if not uid and not name:
            raise FindexException("invalid parameters")

        if uid and not isinstance(uid, int):
            raise FindexException("invalid parameters")

        if name and not isinstance(name, str):
            raise FindexException("invalid parameters")

        if uid:
            query = query.filter(ResourceGroup.id == id)

        if name:
            query = query.filter(ResourceGroup.name == name)

        return query.first()

