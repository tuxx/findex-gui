import re,sys,os
from time import sleep
from gevent.threadpool import ThreadPool

from findex_gui.db.orm import Tasks


class TaskController():
    def __init__(self, db):
        self.db = db

    def add(self, name, desc, method, added, data, resource_prefix):
        owner = 1
        task_exec = 'frontend-1'

        t = Tasks(
            name=name,
            desc=desc,
            method=method,
            added=added,
            data=data,
            resource_prefix=resource_prefix,
            task_exec=task_exec,
            owner=owner
        )

        self.db.add(t)
        self.db.commit()

    def modify(self, task_id, **kwargs):
        owner = 1
        task_exec = 'frontend-1'

        t = self.db.query(Tasks).filter_by(Tasks.id == task_id)
        if not t:
            return

        for k, v in kwargs.iteritems():
            try:
                setattr(t, k, v)
            except:
                pass

        self.db.commit()