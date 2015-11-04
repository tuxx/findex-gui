from gevent import monkey
monkey.patch_all()

import psycogreen.gevent
psycogreen.gevent.patch_psycopg()

import psycopg2


class Postgres():
    def test_connection(self, dbname, user, host, port, password):
        try:
            with psycopg2.connect("dbname='%s' user='%s' host='%s' port='%s' password='%s'" % (
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
        except Exception as ex:
            return {'result': False, 'message': str(ex)}