# Installation (Debian Jessie)

Installing Findex can be a little bit of a pain due to multiple software packages involved with specific version requirements. This document tries to describe all the steps involved in getting the following up and running:

- Python **3.5**
- Postgres **9.5** (on x86_64 Linux)
- ElasticSearch **1.7.6**
- ZomboDB **3.1.12**
- Findex-gui (web-interface)


## Python

First, install Python 3.5. At the time of writing, Python 3.5 is not yet included in the stable repositories for Debian Jessie, so I wrote [a bash script](https://gist.github.com/skftn/be58f8e4cc2afac7cfac34e536a7128c) that should work for you.

After Python 3.5 is installed (should be present at `/usr/bin/python3.5`), install the following:

```sh
sudo apt-get install -y libpq-dev python-virtualenv
```

## Findex

`findex-gui` is available as a [Python package](https://pypi.python.org/pypi/Findex-GUI) through pypi. First create a virtualenv:

```sh
cd ~/
virtualenv -p /usr/bin/python3.5 findex
cd findex
source bin/activate
```

Inside the virtualenenv we can use `pip` to install `findex-gui`:
```sh
pip install findex-gui
```

Now that the web interface is installed, we need to make sure Postgres/Elasticsearch is running and have the ZomboDB module enabled.

## Postgres

In order to install Postgres `v9.5` we need to add the official postgres Debian repository to `/etc/apt/sources/sources.list`. Add this line:

```
deb http://apt.postgresql.org/pub/repos/apt/ jessie-pgdg main
```

Add the key and update:
```sh
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
apt-get update
```

If everything went OK, you can now install Postgres `v9.5`.

```sh
apt-get install postgresql-9.5 postgresql-client-9.5 
```

At which point it is time to set up an user and database:

```sh
sudo su postgres
psql
```

```sql
create database findex;
CREATE USER findex WITH PASSWORD 'changeme';
GRANT ALL PRIVILEGES ON DATABASE "findex" to findex;
ALTER USER findex WITH SUPERUSER;
```

Then restart Postgres:

```sh
sudo service postgresql restart
```

## ElasticSearch 1.7

ElasticSearch runs on java. First grab the jdk from [here](http://download.oracle.com/otn-pub/java/jdk/8u131-b11/d54c1d3a095b4ff2b6607d096fa80163/jdk-8u131-linux-x64.tar.gz) (Linux x64 .tar.gz).

```sh
# the version you downloaded might not be '8u121' - change accordingly
tar -xvzf jdk-8u121-linux-x64.tar.gz
mkdir /usr/lib/jvm
mv jdk1.8.0_121 /usr/lib/jvm/

sudo update-alternatives --install /usr/bin/javac javac /usr/lib/jvm/jdk1.8.0_121/bin/javac 1
sudo update-alternatives --install /usr/bin/java java /usr/lib/jvm/jdk1.8.0_121/bin/java 1
sudo update-alternatives --install /usr/bin/javaws javaws /usr/lib/jvm/jdk1.8.0_121/bin/javaws 1

sudo update-alternatives --config javac 
sudo update-alternatives --config java 
sudo update-alternatives --config javaws
```

Confirm that java is working:
```sh
java -version
```

Now we can fetch and install ElasticSearch `v1.7.6`
```sh
wget https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.7.6.deb
dpkg -i elasticsearch-1.7.6.deb
```

Open `/etc/elasticsearch/elasticsearch.yml` and add/change the following:

```yml
network.bind_host: 127.0.0.1

threadpool.bulk.queue_size: 1024
threadpool.bulk.size: 12

http.compression: true
http.max_content_length: 1024mb

index.query.bool.max_clause_count: 1000000
```

Restart ElasticSearch:

```sh
sudo service elasticsearch restart
```

Confirm that it is running:

```sh
curl http://localhost:9200
```

**warning**: this command might not work due to elasticsearch still starting up - wait at least 10 seconds after restarting ElasticSearch before querying it.

## ZomboDB

Next up is installing [ZomboDB](https://github.com/zombodb/zombodb) as a plugin/module for both ElasticSearch and Postgres.

For ElasticSearch, execute the following:
```sh
cd /tmp && wget https://github.com/zombodb/zombodb/releases/download/v3.1.12/zombodb-es-plugin-3.1.12.zip
/usr/share/elasticsearch/bin/plugin -i zombodb -u file:///tmp/zombodb-es-plugin-3.1.12.zip
sudo service elasticsearch restart
```

For Postgres, execute the following:
```sh
cd /tmp && wget https://github.com/zombodb/zombodb/releases/download/v3.1.12/zombodb_jessie_pg95-3.1.12_amd64.deb
sudo dpkg -i zombodb_jessie_pg95-3.1.12_amd64.deb
```

A small change is needed to `/etc/postgresql/9.5/main/postgresql.conf`, add the following at the end of the file:

```conf
local_preload_libraries = 'zombodb.so'
```

Restart Posgres:

```
sudo service postgresql restart
```

ZomboDB is now correctly installed.

## Configuring findex-gui

We're almost there. Our database is setup and ready for usage. Now we need to configure `findex` so it knows where the database is.

First, activate the virtualenv. If you followed the previous steps literally, the virtualenv should be located over at `~/findex/`. Activate the virtualenv in your shell by executing the following:

```sh
source ~/findex/bin/activate
```


type `findex` to generate configuration. By default, the configuration files will end up in `~/.findex/conf/`. 

Open up `~/.findex/conf/findex.conf` and modify `connection =` so it points to your postgres database.

```conf
connection = postgresql://findex:changeme@localhost:5432/findex
```

Also modify `default_root_password` and `default_anon_password`. These will be the passwords used by the user accounts within the web application.

Finally, execute the following to run the web interface. 

```sh
findex web runserver
```

On a first run, it will create all of the neccesary tables, types and indexes for you.

You now have the web interface running. If you actually want to start crawling servers, you should look at how to install the crawl bots [here](https://github.com/skftn/findex-crawl).

For more information on how to run the web interface, check out [Web interface](https://github.com/skftn/findex-gui/blob/master/docs/web/WEB.md)

### Error: Ran out of servers

This means that for some reason Findex could not connect to the Postgres database. Either it is not running, or not accepting connections. Double check the Findex configuration and the Postgres `pg_hba.conf` file.

### Error: Connection refused

This means ElasticSearch was not running at the time the web interface tried to create the tables.

```
sqlalchemy.exc.InternalError: (psycopg2.InternalError) libcurl error-code: Couldn't connect to server(7); message: Failed to connect to localhost port 9200: Connection refused; req=-XDELETE http://localhost:9200//tieten5.public.files.idx_zdb_files 
```

This leaves the database in a broken state and requires you to drop and re-create the database:

```sh
sudo su postgres
psql

drop database findex;
create database findex;
```

```sh
sudo service elasticsearch restart
```

## Final word

If you encountered any problem during these steps and you are stuck, do not hesitate to submit an issue [here](https://github.com/skftn/findex-gui/issues).