Web interface
=============

Findex provides a full-fledged web interface in the form of a Flask
application. This interface will allow you to submit crawl tasks, browse
through the servers, and search across all the discovered files.

Configuration
-------------

Some additional configuration options exist in the
`$CWD/web/local_settings.py` configuration file.

It is recommended to keep the `DEBUG` variable at `no` in production
setups.

Starting the Web Interface
--------------------------

In order to start the web interface, you can simply run the following
command:

    $ findex web runserver

If you want to configure the web interface as listening for any IP on a
specified port, you can start it with the following command (replace
PORT with the desired port number):

    $ findex web runserver 0.0.0.0:PORT

Or directly without the `runserver` part as follows while also
specifying the host to listen on:

    $ findex web -H 0

### Web Deployment

While the default method of starting the Web Interface server works fine
for many cases, some users may wish to deploy the server in a more
robust manner. This can be done by exposing the Web Interface as a WSGI
application to a web server. This section shows a simple example of
deploying the Web Interface via [uWSGI] and [nginx][uWSGI]. These
instructions are written with Ubuntu GNU/Linux in mind, but may be
adapted to other platforms.

This solution requires `uWSGI`, the `uWSGI Python plugin`, and `nginx`.
All are available as packages:

    $ sudo apt-get install uwsgi uwsgi-plugin-python nginx

#### uWSGI setup

First, use uWSGI to run the Web Interface server as an application.

To begin, create a uWSGI configuration file at
`/etc/uwsgi/apps-available/findex-gui.ini` that contains the actual
configuration as reported by the `findex web --uwsgi` command, e.g.:

    $ findex web --uwsgi
    [uwsgi]
    plugins = python
    virtualenv = /home/findex/findex
    module = findex.web.web.wsgi
    uid = findex
    gid = findex
    static-map = /static=/home/..somepath..
    # If you're getting errors about the PYTHON_EGG_CACHE, then
    # uncomment the following line and add some path that is
    # writable from the defined user.
    # env = PYTHON_EGG_CACHE=
    env = FINDEX_APP=web
    env = FINDEX_CWD=/home/..somepath..

This configuration inherits a number of settings from the distribution’s
default uWSGI configuration and imports `findex.web.wsgi` from the
Findex package to do the actual work. In this example we installed
Cuckoo in a virtualenv located at `/home/findex/findex`. If Cuckoo is
installed globally no virtualenv option is required (and
`findex web --uwsgi` would not report one).

Enable the app configuration and start the server.

``` {.sourceCode .bash}
$ sudo ln -s /etc/uwsgi/apps-available/findex-web.ini /etc/uwsgi/apps-enabled/
$ sudo service uwsgi start findex-web    # or reload, if already running
```

<div class="admonition note">

Logs for the application may be found in the standard directory for
distribution app instances, i.e., `/var/log/uwsgi/app/findex-web.log`.
The UNIX socket is created in a conventional location as well,
`/run/uwsgi/app/findex-web/socket`.

</div>

nginx setup
===========

With the Web Interface server running in uWSGI, nginx can now be set up
to run as a web server/reverse proxy, backending HTTP requests to it.

To begin, create a nginx configuration file at
`/etc/nginx/sites-available/findex-web` that contains the actual
configuration as reported by the `findex web --nginx` command:

    $ findex web --nginx
    upstream _uwsgi_findex_web {
        server unix:/run/uwsgi/app/findex-web/socket;
    }

    server {
        listen localhost:8000;

        # Cuckoo Web Interface
        location / {
            client_max_body_size 1G;
            uwsgi_pass  _uwsgi_findex_web;
            include     uwsgi_params;
        }
    }

Make sure that nginx can connect to the uWSGI socket by placing its user
in the **findex** group:

    $ sudo adduser www-data findex

Enable the server configuration and start the server.

``` {.sourceCode .bash}
$ sudo ln -s /etc/nginx/sites-available/findex-web /etc/nginx/sites-enabled/
$ sudo service nginx start    # or reload, if already running
```

At this point, the Web Interface server should be available at port
**8000** on the server. Various configurations may be applied to extend
this configuration, such as to tune server performance, add
authentication, or to secure communications using HTTPS. However, we
leave this as an exercise for the user.