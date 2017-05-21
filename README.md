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

### Installation

Docker containers will be provided soon. For now, don't attempt to manually install. You've been warned! :)

[Manual installation](https://github.com/skftn/findex-gui/blob/master/INSTALL.md)

### Streetcred
- Volkskrant (http://i.imgur.com/9oqlKU2.png) (dutch)
- Security.nl (dutch): [Duizenden openstaande FTP-servers in Nederland](https://www.security.nl/posting/440684)
- Motherboard (dutch) [440 terabytes aan Nederlandse privébestanden zijn nu makkelijk doorzoekbaar](https://motherboard.vice.com/nl/article/440-terabytes-aan-nederlandse-privbestanden-zijn-nu-makkelijk-doorzoekbaar)
- [@hdmoore](http://i.imgur.com/nyP0EEq.png)
