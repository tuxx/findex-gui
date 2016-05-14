# Findex-GUI

Findex is a platform for finding and indexing files over multiple protocols. The platform consists of 3 individual python packages:

  - `findex-gui` - provides the front-end in the form of a `flask` web application.
  - `findex-crawl` - provides the crawl bot(s) that are responsible for crawling resources.
  - `findex-common` - provides utitilies used by both the GUI and crawl instances.


### Project status
Findex is still in development. Forking the project is not recommended as the documentation has not been written yet and essential parts of the code are still subject to change.
  - `findex-gui` - functional
  - `findex-crawl` - somewhat functional
  - `findex-common` - functional

The only thing that still needs to be added is the functionality to add crawl jobs (point your bots to a FTP/HTTP server).
As this is obviously an important feature for an indexer, please wait before trying to get this to run.

### Findex Features

  - Crawl HTTP open directories (webdav)(BASIC/DIGEST)
  - Crawl FTP servers
  - Distributed crawling with optional RabbitMQ AMQP messaging
  - Bootstrap 3.1.1 file browser.

### Example
[http://findex.cedsys.nl](http://findex.cedsys.nl)

### Requirements:
  - Linux (Debian >= **7** | Ubuntu >= **11** | CentOS >= **6**)
  - Python >= **2.7.3**
  - Postgres >= **9.4**
  - `findex-common` >= **0.2.4**

### Installation
There is no documentation yet. 

### Authors
Maintained by Sander Ferdinand of [CedSys](http://www.cedsys.nl).

### License

`findex-gui` is distributed under the MIT license.