from findex_gui.web import db, app
from findex_gui.controllers.user.user import UserController
from findex_gui.controllers.user.roles import role_req, check_role
from findex_gui.orm.models import Task, ResourceGroup
#from findex_gui.orm.connect import Postgres
from findex_common.exceptions import FindexException, DatabaseException


class TaskController:
    @staticmethod
    @role_req("ADMIN")
    def add_task(name, owner_id=None, options=None, log_error=True, **kwargs):
        if not isinstance(owner_id, int):
            owner = UserController.get_current_user()
        else:
            owner = UserController.user_view(uid=owner_id)
            if not owner:
                raise FindexException("faulty owner_id")
        if not isinstance(name, str):
            raise FindexException("faulty parameters")
        if not isinstance(options, dict):
            options = {}

        task = Task(name=name, owner=owner)

        default_options = {
            "interval": 10800,  # in seconds, 10800 = 3 hours
            "retry": 5,  # times
        }

        for k, v in options.items():
            default_options[k] = v

        task.options = default_options

        try:
            db.session.add(task)
            db.session.commit()
            db.session.flush()
            return task
        except Exception as ex:
            db.session.rollback()
            return DatabaseException(ex, log_error)

    @staticmethod
    def get_task(uid=None, name=None, log_error=True):
        """
        :param uid: task id
        :param name: task name
        :param log_error: log errors to stderr
        :return:
        """
        if not uid and not name:
            raise FindexException("faulty parameters", log_error)

        if uid and not isinstance(uid, int):
            raise FindexException("faulty parameters", log_error)

        if name and not isinstance(name, str):
            raise FindexException("faulty parameters", log_error)

        task = None
        if uid:
            return db.session.query(Task).filter(Task.id == uid).first()

        if name:
            return db.session.query(Task).filter(Task.name == name).first()

    @staticmethod
    def get_tasks(by_owner=None):
        query = db.session.query(Task)
        if by_owner:
            query = query.filter(Task.created_by_id == by_owner)
        all = query.all()
        return all

    @staticmethod
    @role_req("ADMIN")
    def assign_resource_group(task_id, resourcegroup_id, log_error=True, **kwargs):
        """
        :param task_id: task id
        :param resourcegroup_id: resource group id
        :param ignore_constraint_conflict: ignores database constraint errors (postgres only)
        :param log_error: log errors to stderr
        :param kwargs:
        :return:
        """
        if not isinstance(resourcegroup_id, int):
            raise FindexException("faulty parameters", log_error)

        task = TaskController.get_task(uid=task_id)

        group = db.session.query(ResourceGroup).filter(ResourceGroup.id == resourcegroup_id).first()
        if not group or isinstance(group, Exception):
            raise FindexException("Could not fetch resource id \"%d\"" % resourcegroup_id, log_error)

        # check if group is already present in task
        if [z for z in task.groups if z.id == group.id]:
            raise FindexException("Group \"%d\" is already a member of task id \"%d\"" % (resourcegroup_id, task_id), log_error)
        try:
            task.groups.append(group)
            db.session.commit()
            db.session.flush()
        except Exception as ex:
            db.session.rollback()
            raise DatabaseException(ex, log_error)

    @staticmethod
    @role_req("ADMIN")
    def remove_resource_group(task_id: int, resourcegroup_id: int, **kwargs):
        if not isinstance(task_id, int) or not isinstance(resourcegroup_id, int):
            raise FindexException("faulty parameters")
        # @TODO: actually make this function
