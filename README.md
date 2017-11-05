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
  - Linux (Debian >= **7** | Ubuntu >= **11** | CentOS >= **6**)
  - Python >= **3.5**
  - Postgres **9.5**
  - ElasticSearch **1.7.6**
  - RabbitMQ >= **3.5.4**


### Screenshot
[![pic](http://i.imgur.com/WpTTkxx.png)](w0w)

Installation
------------

**warning: findex is still in development and not in alpha mode.**

The easiest way to get findex up and running is via Vagrant. This will create a single virtual machine running Findex.

To get up and running, make sure you have the correct versions installed:

```sh
$ ansible --version
ansible 2.3.2.0

$ vagrant -v
Vagrant 2.0.0

$ virtualbox -h
Oracle VM VirtualBox Manager 5.1.3
(however, can be a lower version)
```

Bring the machine up.

```sh
$ vagrant up findex
```

The web interface can now be reached: `http://192.168.1.13`

Login to the admin interface:

1. Go to `/login`
2. username: `root` pass: `changeme`
3. Go to `/admin`

As previously mentioned, findex is still in development.

### Manual install
[manual installation](https://github.com/skftn/findex-gui/blob/master/docs/INSTALL.md) (not recommended).
