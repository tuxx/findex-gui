# from findex_gui import app
# from flask import render_template
#
#
# @app.route('/')
# def install():
#     return render_template('_setup/templates/setup.html')
#
#
# @app.route('/api/findex/writecfg')
# def writecfg():
#     expected = [
#         'database_host',
#         'database_port',
#         'database_database',
#         'database_username',
#         'database_password',
#         'database_type',
#         'database_type',
#         'gui_bind_host',
#         'gui_bind_port'
#     ]
#
#     params = bottle.request.params.dict
#     data = {}
#
#     for k, v in params.iteritems():
#         if not k in expected:
#             return {
#                 'findex/writecfg': {
#                     'status': 'FAIL',
#                     'message': 'missing %s param' % k
#                 }
#             }
#         else:
#             if not v[0]:
#                 return {
#                     'findex/writecfg': {
#                         'status': 'FAIL',
#                         'message': 'missing value for %s' % k
#                     }
#                 }
#
#             spl = k.split('_', 1)
#             section = spl[0]
#             key = spl[1]
#             val = v[0]
#
#             self.cfg[section][key] = val
#
#     if self.cfg['database']['type'] == 'psql':
#         from findex_gui.db.db import Postgres as psql
#
#         connection = psql().test_connection(
#             dbname=self.cfg['database']['database'],
#             user=self.cfg['database']['username'],
#             host=self.cfg['database']['host'],
#             port=self.cfg['database']['port'],
#             password=self.cfg['database']['password']
#         )
#
#         if not connection['result']:
#             return {
#                 'findex/writecfg': {
#                     'status': 'FAIL',
#                     'message': connection['message']
#                 }
#             }
#
#     # to-do: change these for production
#     self.cfg['gui']['debug'] = False
#     self.cfg['database']['debug'] = True
#
#     self.cfg.write()
#
#     self.main()
#
#     return {
#         'findex/writecfg': {
#             'status': 'OK'
#         }
#     }