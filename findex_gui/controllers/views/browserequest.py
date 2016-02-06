from urllib import quote_plus, unquote_plus, quote, unquote
from datetime import datetime

from findex_gui.db.orm import Files, Resources
from findex_gui.controllers.findex.findex import Findex

from findex_common.bytes2human import bytes2human
from findex_common.exceptions import BrowseException
from findex_common.resourcetypes import get_protocol_from_int


# to-do: rewrite
class BrowseRequest():
    def __init__(self, db, findex):
        self.db = db
        self.findex = findex

        self.data = {}

    def parse(self, path):
        self.data['isdir'] = path.endswith('/')

        self.data['path_spl'] = path.split('/')
        self.data['identifier'] = self.data['path_spl'][0].lower()
        self.data['file_path'] = '/' + '/'.join(self.data['path_spl'][1:-1])

        if self.data['file_path'] != '/':
            self.data['file_path'] += '/'

        if not self.data['isdir']:
            self.data['file_name'] = path.split('/')[-1]
        else:
            self.data['file_name'] = self.data['path_spl'][-2] if len(self.data['path_spl']) > 1 else ''

        if not ':' in self.data['identifier']:
            raise BrowseException('No : in resource_name')

        address, port = self.data['identifier'].split(':', 1)
        resource = self.findex.get_resources(address=address, port=port)

        if not resource:
            raise BrowseException('No resource found')

        self.data['resource'] = resource

    def fetch_files(self, **kwargs):
        files = self.findex.get_files(
            resource_id=self.data['resource'].id,
            file_path=self.data['file_path'],
            **kwargs)

        if not files:
            # to-do: rewrite
            try:
                file_path = '/%s' % ('/'.join([z for z in self.data['path_spl'][1:] if z][:-1]))
                if len(file_path) > 1:
                    file_path += '/'

                files = self.findex.get_files(
                    resource_id=self.data['resource'].id,
                    file_path=file_path
                )

                ok = [z for z in files if z.file_name == self.data['file_name'] and z.file_isdir][0]
                if ok:
                    return []
            except:
                pass

            raise BrowseException('No file(s) found')

        return files

    def prepare_files(self, files, env, sort=None):
        # sort files
        files = sorted(files, key=lambda k: k.file_name)  # alphabetically
        files = sorted(files, key=lambda k: k.file_isdir, reverse=True)  # folders always on top

        if not self.data['file_path'] == '/' and self.data['isdir']:  # add CDUP dirs
            files.insert(0, self._cdup_dir())

        for f in files:
            if self.data['resource'].protocol in [4,5]:
                if not self.data['isdir']:
                    protocol = get_protocol_from_int(self.data['resource'].protocol)

                    url = '%s://%s:%s%s%s' % (
                        protocol,
                        self.data['resource'].address,
                        int(self.data['resource'].port),
                        self.data['resource'].basepath,
                        f.file_url)
                else:
                    url = f.file_name
            else:
                url = f.file_name_human
                if f.file_isdir:
                    url += '/'

            setattr(f, 'href', url)

        return self.findex.set_icons(env=env, files=files)

    def _cdup_dir(self):
        cdup = Files(
            file_name='..',
            file_path='../',
            file_ext='',
            file_format=-1,
            file_isdir=True,
            file_modified=datetime.now(),
            file_perm=None,
            searchable=None,
            file_size=0,
            resource_id=self.data['resource'].id
        )

        setattr(cdup, 'file_name_human', '..')
        return cdup

    def action_fetches(self):
        if not self.data['resource'].protocol in [0,4]:
            return

        url = '%s' % self.data['resource'].display_url

        if self.data['file_path'] == '/':
            path = ''
        elif self.data['file_path'].startswith('/') and url.endswith('/'):
            path = self.data['file_path'][1:]

        wget_extras = ''
        lftp_extras = ''

        # if self.source.crawl_authtype:
        #     wget_extras = 'user=%s password=%s ' % (self.source.crawl_username, self.source.crawl_password)
        #
        #     if self.source.crawl_authtype == 'HTTP_DIGEST':
        #         lftp_extras = Debug('Authentication using DIGEST is not supported by lftp')
        #     else:
        #         lftp_extras = '-u %s,%s ' % (self.source.crawl_username, self.source.crawl_password)

        wget = 'wget %s-r -nH --no-parent \'%s\'' % (wget_extras, url + self.data['file_path'])
        lftp = 'lftp %s-e \'mirror\' \'%s\'' % (lftp_extras, url + self.data['file_path'])

        return dict(wget=wget, lftp=lftp)

    def breadcrumbs(self):
        data = [self.data['identifier']]
        data += [z for z in self.data['file_path'].split('/')[1:] if z]

        return data

    # to-do: crawler should take notice of dir sizes
    # def sort(self, files):
    #     # calculate total folder file size (non-recursive)
    #     total_size = 0
    #     for f in files:
    #         total_size += f.file_size

    # def output_json(self):
    #     data = []
    #
    #     for source_file in self.files:
    #         if source_file.filename_human == '..':
    #             continue
    #
    #         data.append('[%s] %s%s%s' % (
    #             'D' if source_file.is_directory else 'F',
    #             self.folder.source.crawl_url,
    #             source_file.filepath_human,
    #             source_file.filename_human))
    #
    #     return '\n'.join(data)