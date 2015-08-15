# Findex-GUI

Findex is a platform for finding and indexing files over multiple protocols. It tries to be fast, customizable and scaleable. The platform consists of 3 individual python packages:

  - `findex-gui` - provides the front-end in the form of a `bottle.py` web application.
  - `findex-crawl` - provides the crawl bot(s) that are responsible for crawling resources.
  - `findex-common` - provides utitilies used by both the GUI and crawl instances.


### Project status
Findex is still in development. It is not recommended you try to install Findex as the documentation has not been written yet and essential parts of the code are still sensitive to change.
  - `findex-gui` - somewhat functional
  - `findex-crawl` - somewhat functional
  - `findex-common` - useable

### Features

  - Crawl HTTP open directories (webdav)(BASIC/DIGEST)
  - Crawl FTP/SMB servers
  - Distributed crawling with RabbitMQ AMQP messaging
  - Bootstrap 3.1.1 file browser.

### Example
[http://findex.cedsys.nl](http://findex.cedsys.nl)

### Requirements:
  - Linux (Debian >= 7 | Ubuntu >= 11 | CentOS >= 6)
  - Python >= 2.7.3
  - Postgres >= 9.4
  - RabbitMQ >= 3.5.4 (optional)
  - The *findex-common* package

### Installation
Please visit the [Documentation](https://github.com/no_documentation_yet). For those in a hurry:
```sh
$ apt-get install python-virtualenv python-pip
```

```sh
$ pip install findex-common

# if you have not yet made a virtualenv yet, make one
$ virtualenv findex && cd $_ && source bin/activate
# if you have previously made a virtualenv for findex, cd and activate it
$ cd /path/to/findex_virtualenv/ && source bin/activate

# clone and install findex-gui
(findex)$ git clone <repo> 
(findex)$ cd findex-gui
(findex)$ python setup.py install
```
You can now start Findex by typing `service findex start`. If the above failed, it is a good idea to check out the [installation guide](https://github.com/skftn/findex-crawl).

### Python plugins used
* findex-common
* python-dateutil
* psycopg2
* jinja2
* sqlalchemy
* gevent
* bottle
* bottle-sqlalchemy
* psycogreen

### Authors
Maintained by Sander Ferdinand of [CedSys](http://www.cedsys.nl).
### License

`findex-gui` is distributed under the MIT license.