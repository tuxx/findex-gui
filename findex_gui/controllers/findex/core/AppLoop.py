import re,sys,os, bottle
from time import sleep

from gevent.threadpool import ThreadPool
from sqlalchemy.orm import sessionmaker

from findex_gui.controllers.findex.amqp import AmqpController
from findex_gui.controllers.findex.tasks import TaskController
from findex_gui.controllers.findex.themes import ThemeController
from findex_gui.controllers.findex.cache import CacheController
from findex_gui.db.orm import Options


class AppLoop():
    def __init__(self, engine):
        self.engine = engine

        self._ifaces = {
            'amqp': [AmqpController, 300],
            'themes': [ThemeController, 300],
            'cache': [CacheController, 300]
        }

        self._pool = ThreadPool(len(self._ifaces.keys())+1)
        self._pools = []

    def start(self):
        ses = sessionmaker(bind=self.engine)()

        for k, v in self._ifaces.iteritems():
            bottle.loops[k] = v[0](ses)
            sleep(1)
            self._pools.append(self._pool.spawn(self._loop, k, v[1]))

    def _loop(self, name, interval):
        while True:
            bottle.loops[name].loop()
            sleep(interval)