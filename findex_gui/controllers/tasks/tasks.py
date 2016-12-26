from findex_gui import db
from findex_gui.controllers.user.user import UserController
from findex_gui.controllers.user.roles import role_req, check_role
from findex_gui.orm.models import Task, ResourceGroup
from findex_common.exceptions import FindexException, DatabaseException


class TaskController:
    @staticmethod
    @role_req("ADMIN")
    def add_task(name, owner_id=None, options={}, **kwargs):
        if not isinstance(owner_id, int):
            owner = UserController.get_current_user()
        else:
            owner = UserController.user_view(uid=owner_id)
            if not owner:
                raise FindexException("faulty owner_id")

        if not isinstance(name, (str, unicode)):
            raise FindexException("faulty parameters")

        task = Task(name=name, owner=owner)

        default_options = {
            "interval": 10800,  # in seconds, 10800 = 3 hours
            "retry": 5,  # times
        }

        for k, v in options.iteritems():
            default_options[k] = v

        task.options = default_options

        try:
            db.session.add(task)
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            return DatabaseException(ex)

    @staticmethod
    def get_tasks(by_owner=None):
        query = db.session.query(Task)
        if by_owner:
            query = query.filter(Task.created_by_id == by_owner)
        all = query.all()
        return all

    @staticmethod
    @role_req("ADMIN")
    def assign_resource_group(task_id, resourcegroup_id, **kwargs):
        if not isinstance(task_id, int) or not isinstance(resourcegroup_id, int):
            raise FindexException("faulty parameters")

        task = db.session.query(Task).filter(Task.id == task_id).first()
        if not task or isinstance(task, Exception):
            raise FindexException("Could not fetch task id \"%d\"" % task_id)

        group = db.session.query(ResourceGroup).filter(ResourceGroup.id == resourcegroup_id).first()
        if not group or isinstance(group, Exception):
            raise FindexException("Could not fetch resource id \"%d\"" % resourcegroup_id)

        # check if group is already present in task
        if [z for z in task.groups if z.id == group.id]:
            raise FindexException("Group \"%d\" is already a member of task id \"%d\"" % (resourcegroup_id, task_id))
        try:
            task.groups.append(group)
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            return DatabaseException(ex)

    @staticmethod
    @role_req("ADMIN")
    def remove_resource_group(task_id, resourcegroup_id, **kwargs):
        if not isinstance(task_id, int) or not isinstance(resourcegroup_id, int):
            raise FindexException("faulty parameters")

