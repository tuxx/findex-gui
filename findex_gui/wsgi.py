from gevent.monkey import patch_all
patch_all()

from psycogreen.gevent import patch_psycopg
patch_psycopg()

from findex_gui.main import findex_init
from findex_gui.bin.misc import cwd, decide_cwd
decide_cwd()
findex_init(level=0, ctx=None)

from findex_gui.web import create_app
app = create_app()
