Findex
========

is a file indexer for FTP, SMB and HTTP servers.

Features
--------
- Scalable/fast
- [Searching](http://i.imgur.com/WpTTkxx.png) (file name, category, size, extension)
- [File browsing](http://i.imgur.com/6UkGBzB.png)
- [Metadata powered 'popcorn' view](https://i.imgur.com/9suQ5mY.png) (release year, director, actors/actresses, genre)
- User login / registration
- Languages: Dutch/English
- Reverse proxying/streaming from the (ftp/http) backends through the web interface

Stack
----------
[Postgres 9.5](https://www.postgresql.org/), [RabbitMQ](https://www.rabbitmq.com/), [ElasticSearch 1.7](https://www.elastic.co/), [ZomboDB](https://github.com/zombodb/zombodb), [Flask](http://flask.pocoo.org/),  [Twisted](https://twistedmatrix.com/trac/)

Requirements
------------
  - Python >= **3.5**
  - Postgres **9.5**
  - ElasticSearch **5.6.4**
  - RabbitMQ >= **3.5.4**
  - Recommended: 4GB RAM, 2 cores


### Screenshot
[![pic](http://i.imgur.com/WpTTkxx.png)](w0w)

Installation
------------

**Findex is still in development.**

The easiest way to get findex up and running is via Vagrant. The following will create:

- Ubuntu 16.04 64bit
- 4GB, 2 cores
- findex-gui, ran via [supervisord](http://supervisord.org/) on port 2010
- Nginx running on port 80 with a `ProxyPass` to `localhost:2010`
- Postgres 9.5
- Elasticsearch 5.6.4
- RabbitMQ

```sh
$ ansible --version
ansible 2.3.2.0

$ vagrant -v
Vagrant 2.0.0

$ virtualbox -h
Oracle VM VirtualBox Manager 5.1.3  <-- (can be a lower version)
```

Bringing the machine up:

```sh
$ vagrant up findex
```

After installation, the web interface can be reached at `http://192.168.1.13`

Login to the admin interface:

1. Go to `/login`
2. username: `root` pass: `changeme`
3. Go to `/admin`

As previously mentioned, findex is still in development.

### Manual install
[manual installation](https://github.com/skftn/findex-gui/blob/master/docs/INSTALL.md) (not recommended / outdated).
