from gevent import monkey
monkey.patch_all()

import psycogreen.gevent
psycogreen.gevent.patch_psycopg()

import psycopg2
import socket


class Postgres():
    def test_connection(self, dbname, user, host, port, password):
        try:

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((host, port))
            s.shutdown(2)

            with psycopg2.connect("dbname='%s' user='%s' host='%s' port='%s' password='%s' connect_timeout=1" % (
                dbname, user, host, port, password
            )) as conn:
                cur = conn.cursor()
                cur.execute("""SELECT extversion from pg_extension where extname='pg_trgm'""")
                rows = cur.fetchone()

                if not rows:
                    return {'result': False, 'message': """
                        Connection to the database was made, however, the Postgres extension 'pg_trgm' is not enabled. Please run "create extension pg_trgm;" as the database administrator in a SQL shell.
                    """.strip()}

                return {'result': True, 'message': 'Connection made.'}

        except socket.timeout:
            return {'result': False, 'message': 'Cannot connect to %s:%s. Is the database up? Firewall?' % (host, str(port))}
        except socket.gaierror:
            return {'result': False, 'message': 'Could not resolve hostname %s' % host}
        except Exception as ex:
            return {'result': False, 'message': str(ex)}