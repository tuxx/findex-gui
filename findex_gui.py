# -*- coding: utf-8 -*-
import settings


def run_synchronous():
    from findex_gui import app
    app.run(debug=settings.app_debug, host=settings.bind_host, port=settings.bind_port, use_reloader=False)


def run_asynchronous():
    from gevent import monkey
    monkey.patch_all()

    from gevent.pywsgi import WSGIServer
    from findex_gui import app

    http_server = WSGIServer((settings.bind_host, settings.bind_port), app)
    print ' * Running on http://%s:%s/ (Press CTRL+C to quit)' % (settings.bind_host, str(settings.bind_port))
    http_server.serve_forever()


if settings.app_async:
    run_asynchronous()
else:
    run_synchronous()
