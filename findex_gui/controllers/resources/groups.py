from sqlalchemy_utils import escape_like

from findex_gui.web import db
from findex_gui.orm.models import Resource, ResourceMeta, ResourceGroup, Server, Mq
from findex_gui.controllers.amqp.amqp import MqController
from findex_gui.controllers.user.roles import role_req


class ResourceGroupController:
    @staticmethod
    @role_req("USER_REGISTERED", "RESOURCE_CREATE")
    def add(name: str, description: str, crawl_interval: int = 86400,
            amqp: str = None, removable: bool = True):
        if not isinstance(crawl_interval, int):
            raise Exception("crawl_interval must be integer")

        group = ResourceGroup(name=name, description=description, removable=removable)
        if isinstance(amqp, str) and amqp:
            mq = MqController.get(name=amqp)
            if not mq:
                raise Exception("could not assign amqp name \'%s\' to new "
                                "resource group because it does not exist")
            group.mq = mq
        db.session.add(group)
        db.session.commit()
        db.session.flush()
        return True

    @staticmethod
    @role_req("USER_REGISTERED", "RESOURCE_CREATE")
    def remove(uid: int):
        if not isinstance(uid, int):
            raise Exception("uid should be int")
        try:
            q = db.session.query(ResourceGroup)
            result = q.filter(ResourceGroup.id == uid).first()
            if not result:
                return True
            elif result.name == "Default" or result.removable is False:
                raise Exception("cant remove this group")
            result.remove()
            db.session.commit()
            db.session.flush()
            return True
        except:
            db.session.rollback()
            raise

    @staticmethod
    @role_req("USER_REGISTERED", "RESOURCE_VIEW")
    def get(uid: int = None, name: str = None, limit: int = None,
            offset: int = None, search: str = None):
        """
        Fetches some resourcegroups
        :param uid:
        :param name:
        :param limit:
        :param offset:
        :param search: performs a fulltext search
        :return:
        """
        q = db.session.query(ResourceGroup)

        if isinstance(uid, int):
            return [q.filter(ResourceGroup.id == uid).first()]

        if isinstance(name, str) and name:
            q = q.filter(ResourceGroup.name == name).first()

        if isinstance(search, str) and search:
            q = q.filter(ResourceGroup.name.ilike("%" + escape_like(search) + "%"))

        if offset and isinstance(offset, int):
            q = q.offset(offset)

        if limit and isinstance(limit, int):
            q = q.limit(limit)

        return q.all()

    @staticmethod
    @role_req("USER_REGISTERED", "RESOURCE_REMOVE", "RESOURCE_CREATE")
    def assign_amqp(resourcegroup_id: int, amqp_id: int):
        """
        Assigns an AMQP broker to a resource group
        :param amqp_id:
        :param resourcegroup_id: e
        :return:
        """
        resourcegroup_id, amqp_id = map(int, [resourcegroup_id, amqp_id])

        rq = db.session.query(ResourceGroup)
        rq = rq.filter(ResourceGroup.id == resourcegroup_id)
        rq = rq.first()

        if not rq:
            raise Exception("ResourceGroup id %d not found" % resourcegroup_id)

        aq = db.session.query(Mq)
        aq = aq.filter(Mq.id == amqp_id)
        aq = aq.first()

        if not aq:
            raise Exception("Mq id %d not found" % amqp_id)

        rq.mq = aq
        db.session.commit()
        db.session.flush()
