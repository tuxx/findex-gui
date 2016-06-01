# Findex-GUI

Findex is a platform for finding and indexing files over multiple protocols. The platform consists of 3 individual python packages:

  - `findex-gui` - provides the front-end in the form of a `flask` web application.
  - `findex-crawl` - provides the crawl bot(s) that are responsible for crawling resources.
  - `findex-common` - provides utitilies used by both the GUI and crawl instances.

### Features

  - Crawl HTTP open directories (webdav)(BASIC/DIGEST)
  - Crawl FTP servers
  - Distributed crawling with RabbitMQ AMQP messaging
  - Bootstrap 3.1.1 file browser.

### Status
**warning:** It is not recommended you clone this repository as it is still in development.


**Backend**

 Feature  |  Status  | Details
---|:---:|---|
 API  | :white_check_mark: | Supported: Search, Browse, Session, Admin
 Users | :white_check_mark: | Supported: Register, Login
 Roles | :clock2: | In development
 Sessions | :white_check_mark: | Supported
 Admin Panel  | :clock2: | In development
 I18n Translations | :white_check_mark: | Supported: English, Dutch
 In-App Crawling  | :clock2: | In development
 RAW/JSON Interface | :x: | Not yet
 WebDav Interface  | :x: | Not yet


**Frontend**

 Feature  |  Status  | Details
---|:---:|---|
Themes  | :white_check_mark:  |  Custom themes supported
Bootstrap | :white_check_mark:  |  v3
jQuery  | :white_check_mark:  |  v1.11.3
ES6 Transpilers | :clock2:  |  In development
Grunt | :x: | Not yet
SCSS/Sass | :x: | Not yet


**Crawling**

 Feature  |  Status  | Details
---|:---:|---|
HTTP|:white_check_mark:|Supported
FTP|:white_check_mark:|Supported
Direct Connect|:x:| Not yet
SMB|:x:| Not yet
SSH|:x:| Not yet


**File Metadata and Performance**

| Feature  | Status  | Details  |
|---|---|---|
Movie Metadata|:clock2:| In development
Image Metadata|:clock2:| In development
Music Metadata|:x:| Not yet
Document Metadata|:x:| Not yet
DB Pools|:white_check_mark:| Supported
Memcached|:clock2:| In development
ES backend|:x:| Not yet
SQLite backend|:x:|Not yet


### Example
[http://findex.cedsys.nl](http://findex.cedsys.nl)

### Requirements:
  - Linux (Debian >= **7** | Ubuntu >= **11** | CentOS >= **6**)
  - Python >= **2.7.3**
  - Postgres >= **9.5**
  - RabbitMQ >= **3.5.4** (optional)
  - `findex-common` >= **0.3.2**

### Installation
Not yet available.

### Authors
Maintained by Sander Ferdinand of [CedSys](http://www.cedsys.nl).

### License

`findex-gui` is distributed under the MIT license.
