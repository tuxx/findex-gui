#!/usr/bin/python
import gevent.monkey
gevent.monkey.patch_all()

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import time, os

from findex_gui.bin.config import FindexGuiConfig
from findex_gui.controllers.findex.app import FindexApp

os.environ['TZ'] = 'Europe/Amsterdam'
time.tzset()

cfg = FindexGuiConfig()
cfg.load()
app = FindexApp(cfg)

if not cfg.items:
    app.routes_setup()
else:
    app.main()

app.bind()