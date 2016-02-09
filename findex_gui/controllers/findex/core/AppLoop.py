import re,sys,os, bottle
from time import sleep

from gevent.threadpool import ThreadPool
from sqlalchemy.orm import sessionmaker

from findex_gui.controllers.findex.amqp import AmqpController
from findex_gui.controllers.findex.tasks import TaskController
from findex_gui.controllers.findex.themes import ThemeController
from findex_gui.db.orm import Options


class AppLoop():
    def __init__(self, engine):
        self.engine = engine
        self._pool = ThreadPool(1)

        self._ifaces = {
            'amqp': [AmqpController, 5],
            'themes': [ThemeController, 5]
        }

    def start(self):
        ses = sessionmaker(bind=self.engine)()

        for k, v in self._ifaces.iteritems():
            bottle.loops[k] = v[0](ses)

            self._pool.spawn(self._loop, k, v[1])

    def _loop(self, name, interval):
        while True:
            bottle.loops[name].loop()

            sleep(interval)