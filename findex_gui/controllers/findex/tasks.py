import re,sys,os
from gevent.threadpool import ThreadPool


class Tasks():
    def __init__(self):
        self.pool = ThreadPool(4)

    def startLoop(self):
        self.pool.spawn(self.loop)

    def loop(self):
        pass

