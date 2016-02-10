import jinja2
from datetime import datetime
from urllib import unquote, quote_plus

from findex_gui.db.orm import Files, Resources
from findex_common.exceptions import SearchException
from findex_gui.controllers.findex.findex import Findex


# to-do: rewrite/refactor
class Searcher():
    def __init__(self, cfg, db, env):
        self.cfg = cfg
        self.db = db
        self.env = env
        self.findex = Findex(self.db)

    def _key_check(self, keyword):
        if isinstance(keyword, dict):
            if not 'key' in keyword or not keyword['key']:
                keyword['key'] = ['']
                #raise SearchException('Search query must contain 1 character or more')

            keyword = keyword['key'][0]

        block = ['-', ',', '+', '_', '%']
        for b in block:
            keyword = keyword.replace(b, ' ')

        # if len(keyword) < 1:
        #     raise SearchException('Search query must contain 1 character or more')

        return keyword

    def search(self, vars):
        val = self._key_check(vars)
        val = val.lower()

        filtered = False
        start_dbtime = datetime.now()

        # to-do: move this to API (or make api.py use this class)
        q = self.db.query(Files)

        # if this is later set with Files.<column_name>, it will be sorted on this.
        sort = ''

        sdata = {
            'protocols': [],
            'hosts': [],
            'exts': [],
            'cats': [],
            'fsize': 0
        }

        if 'protocols' in vars:
            protocols = [z.lower() for z in vars['protocols']]
            plookup = {'ftp': 0, 'http': 1, 'smb': 2}

            protocols_ids = []
            if isinstance(protocols, list):
                protocols = [z.lower() for z in protocols]

                for p in protocols:
                    if p in plookup and not plookup[p] in protocols_ids:
                        protocols_ids.append(plookup[p])

            if protocols_ids:
                sdata['protocols'] = protocols_ids

        else:
            sdata['protocols'] = [0, 1, 2, 3, 4, 5]

        if 'hosts' in vars:
            dhosts = vars['hosts']

            if isinstance(dhosts, list):
                if not dhosts[0] == '*':
                    host_ids = []
                    for host in dhosts:
                        host_query = self.db.query(Resources)
                        if ':' in host:
                            host, port = host.split(':', 1)
                            port = int(port)

                            host_query = host_query.filter(Resources.address == host)
                            host_query = host_query.filter(Resources.port == port)

                        host_query = host_query.filter(Resources.protocol.in_(sdata['protocols']))
                        host_results = host_query.all()

                        for host_result in host_results:
                            host_ids.append(host_result.id)

                    if host_ids:
                        sdata['hosts'] = host_ids
                    else:
                        raise SearchException('Could not find any host entries for specified host(s)')

        if sdata['hosts']:
            q = q.filter(Files.resource_id.in_(sdata['hosts']))
            filtered = True

        if 'cats' in vars:
            clookup = {
                'unknown': 0,
                'documents': 1,
                'movies': 2,
                'music': 3,
                'pictures': 4
            }

            dformats = []
            for cat in [z.lower() for z in vars['cats']]:
                if cat in clookup:
                    dformats.append(clookup[cat])
                else:
                    dformats.append(int(cat))

            if isinstance(dformats, list):
                q = q.filter(Files.file_format.in_(dformats))

                for dformat in dformats:
                    sdata['cats'].append(dformat)
        else:
            sdata['cats'] = [0, 1, 2, 3, 4]

        for i in [0, 1, 2, 3, 4]:
            if not i in sdata['cats']:
                filtered = True

        if 'exts' in vars:
            exts = vars['exts']

            if isinstance(exts, list):
                exts = [z.replace('.', '') for z in exts if z]

                q = q.filter(Files.file_ext.in_(exts))
                filtered = True

                for ext in exts:
                    sdata['exts'].append(ext)
        elif '.' in val:
            spl = val.split('.', 1)
            ext = spl[1].replace(',', '').strip()
            q = q.filter(Files.file_ext == ext)
            sdata['exts'].append(ext)

            val = self._key_check(spl[0])
            filtered = True

        if 'size' in vars:
            fsize = vars['size']

            if isinstance(fsize, list):
                fsize = int(fsize[0])

                sizes = {
                    0: '*',
                    1: (0, 8388600),
                    2: (8388600, 134220000),
                    3: (134220000, 536870912),
                    4: (536870912, 2147483648),
                    5: (2147483648, 8589934592),
                    6: (8589934592)
                }

                if fsize == 0:
                    pass
                elif 1 <= fsize <= 5:
                    q = q.filter(Files.file_size > sizes[fsize][0], Files.file_size < sizes[fsize][1])
                    filtered = True
                elif fsize == 6:
                    q = q.filter(Files.file_size > sizes[fsize])
                    filtered = True

                sdata['fsize'] = fsize
                sort = 'file_size'

        if 'path' in vars:
            path = vars['path']

            if isinstance(path, list) and len(path) > 0:
                path = path[0]

                if len(path) > 3:
                    path = unquote(path)
                    q = q.filter(Files.file_path.like(path+'%'))
                    filtered = True

        if 'host' in vars:
            host = vars['host']

            if isinstance(host, list):
                host = int(host[0])
                q = q.filter(Files.resource_id == host)
                filtered = True

        q = q.filter(Files.searchable.like('%'+val+'%')).limit(600)

        results = {}
        results['data'] = q.all()
        results['load_dbtime'] = (datetime.now() - start_dbtime).total_seconds()

        if sort:
            results['data'] = sorted(results['data'], key=lambda k: k.file_size, reverse=True)

        # to-do: dont do this here
        for r in results['data']:
            host = self.findex.get_resources(r.resource_id)
            setattr(r, 'resource', host)

        results['data'] = self.findex.set_humanize(results['data'])
        results['data'] = self.findex.set_icons(env=self.env, files=results['data'])
        sdata['filtered'] = filtered

        return {'sdata': sdata, 'results': results, 'key': jinja2.escape(vars['key'][0])}