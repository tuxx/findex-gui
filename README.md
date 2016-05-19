# Findex-GUI

Findex is a crawler for FTP servers and SMB shares. It provides a web interface for searching files.

  - `findex-gui` - provides the front-end in the form of a `flask` web application.
  - `findex-crawl` - provides the crawl bot(s) that are responsible for crawling resources.
  - `findex-common` - provides utitilies used by both the GUI and crawl instances.


### Project status
Findex is still in development. Forking/Cloning the project is not recommended!
  - `findex-gui` - functional but WIP
  - `findex-crawl` - functional
  - `findex-common` - functional

### Findex Features

  - Crawl HTTP open directories (webdav)(BASIC/DIGEST)
  - Crawl FTP servers
  - Crawl SMB shares
  - Optional distributed crawling with AMQP (RabbitMQ) messaging
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