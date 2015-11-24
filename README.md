# Findex-GUI

Findex is a platform for finding and indexing files over multiple protocols. The platform consists of 3 individual python packages:

  - `findex-gui` - provides the front-end in the form of a `bottle.py` web application.
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
  - Distributed crawling with RabbitMQ AMQP messaging
  - Bootstrap 3.1.1 file browser.

### Example
[http://findex.cedsys.nl](http://findex.cedsys.nl)

### Requirements:
  - Linux (Debian >= **7** | Ubuntu >= **11** | CentOS >= **6**)
  - Python >= **2.7.3**
  - Postgres >= **9.4**
  - RabbitMQ >= **3.5.4** (optional)
  - `findex-common` >= **0.2.3**

### Installation
There is no documentation yet. However; if you want to install it anyway, follow these steps:

First fetch the required system packages.
```sh
$ apt-get install python-virtualenv python-pip libpq-dev
```
Install or upgrade the latest findex-common package (version 0.2.3 is latest).
```sh
$ pip install findex-common
or
$ pip install --upgrade findex-common
```
Make a virtualenv for Findex.
```
# for new installations
$ virtualenv findex && cd $_ && source bin/activate

# if you have previously made a virtualenv for findex, activate it:
$ cd /path/to/findex_virtualenv/
$ source bin/activate
```
Inside the virtualenv, we can clone this repository and install it.
```
(findex)$ git clone <repo> 
(findex)$ cd findex-gui
(findex)$ python setup.py install
```
Make a configuration file under `/etc/findex/gui.cfg`. Use [this file](https://raw.githubusercontent.com/skftn/findex-gui/master/gui.cfg.example) as an example. 

After the configuration file is in place you can start the web application by typing `findex-gui start`. It will bind on the interface and port provided in the configuration file. `findex-gui stop` should be used to stop the process.

### Authors
Maintained by Sander Ferdinand of [CedSys](http://www.cedsys.nl).

### License

`findex-gui` is distributed under the MIT license.
