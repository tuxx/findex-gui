# Findex-GUI

Findex is a high performance platform for finding and indexing files. It tries to be fast, customizable and scaleable. 

[![pic](http://i.imgur.com/WpTTkxx.png)](w0w)

In practical terms, Findex is an over-engineered FTP crawler. You may observe a live example over at [http://findex.cedsys.nl](http://findex.cedsys.nl)

### Goals
- Support the following protocols: FTP, HTTP, SMB (windows), AFP (apple).
- 100% self-hosted, no third-party assets from CDNs to guarantee privacy.
- Should have a API that people can freely query against.
- Searches should be fast (< 500ms), even when the database has more than 100 million rows and at the same time not impose ridiculous hardware requirements.
- Should run on sane software: Linux, Postgres, ECMAScript 6, etc.
- 100% open-source, MIT licensed.

### Software stack
In order to meet the requirements set above, Findex has been designed in a modular fashion for maximum scalability. There are many components involved, some of which are listed below:

- [Postgres 9.5](https://www.postgresql.org/): The main database application.
- [RabbitMQ](https://www.rabbitmq.com/): AMQP message broker provides a way to manage crawl jobs. Individual crawlers subscribe on a queue and may accept or reject incoming crawl tasks.
- [ElasticSearch 1.7](https://www.elastic.co/): While Postgres provides excellent full-text search capabilities through the GIN index, ES is better suited when it comes to Big Data™.
- [ZomboDB](https://github.com/zombodb/zombodb): A Postgres module that syncs data to ElasticSearch.
- [Flask](http://flask.pocoo.org/): A microframework used by the web application. Chosen for its simplicity.
- [Twisted](https://twistedmatrix.com/trac/): Asynchronous networking library that powers the crawl bots.

As for the requirements:
  - Linux (Debian >= **7** | Ubuntu >= **11** | CentOS >= **6**)
  - Python >= **3.5**
  - Postgres **9.5**
  - ElasticSearch **1.7.6**
  - RabbitMQ >= **3.5.4**

## Status

Findex is still in development, however the following things *kinda* work:

- Protocols supported: FTP/HTTP
- [Searching](http://i.imgur.com/WpTTkxx.png) (file name, category, size, extension)
- [File browsing](http://i.imgur.com/6UkGBzB.png)
- [IMDB powered 'popcorn' view](http://i.imgur.com/8nk8rbY.png) (release year, director, actors/actresses, genre)
- User login / registration
- Creating news posts
- Reverse proxy from FTP/HTTP backends to allow video streaming through HTML5 elements

I'd advice against trying to get this to run before any documentation has been written.

### Authors
Maintained by Sander Ferdinand of [CedSys](http://www.cedsys.nl).

### License

MIT