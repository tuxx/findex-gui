Findex
========

is a file indexer for FTP, SMB and HTTP servers.

Features
--------
- Scalable/fast
- [Searching](http://i.imgur.com/WpTTkxx.png) (file name, category, size, extension)
- [File browsing](http://i.imgur.com/6UkGBzB.png)
- [IMDB powered 'popcorn' view](http://i.imgur.com/8nk8rbY.png) (release year, director, actors/actresses, genre)
- User login / registration
- Languages: Dutch/English
- Reverse proxying files from the (ftp/http) backend through the web interface

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

[manual installation](https://github.com/skftn/findex-gui/blob/master/docs/INSTALL.md) (not recommended).

### Vagrant

The easiest way to get findex up and running is via vagrant.

The current Vagrant/ansible configuration spawns 3 machines:

```
192.168.1.10 - findex-gui
192.168.1.11 - Postgres
192.168.1.12 - Elasticsearch
```

To get up and running, make sure you have the correct versions installed:

```sh
$ ansible --version
ansible 2.3.2.0

$ vagrant -v
Vagrant 2.0.0

$ virtualbox -h
Oracle VM VirtualBox Manager 5.1.3
```

Bring up the machines

```sh
$ vagrant up postgres_dev
$ vagrant up elasticsearch_dev
$ vagrant up gui_dev
```

Provision (if necessary, should happen automatically)
```
$ vagrant provision postgres_dev
$ vagrant provision elasticsearch_dev
$ vagrant provision gui_dev
```

Starting the web interface

```
$ vagrant ssh gui
$ sudo su
$ su findex
$ cd ~/findex-gui
$ source venv/bin/activate
$ findex web --host 192.168.1.10 --port 3030
```

The web interface can now be reached: `http://192.168.1.10:3030`

In the future, more versatile deployment options will be provided.
