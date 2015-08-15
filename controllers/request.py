from urllib import quote_plus
import math


class BrowseRequest():
    def __init__(self, request, request_path):
        self.request = request
        self.request_path = request_path

        self.file_name = ''
        self.file_path = ''
        self.source_name = ''
        self.number_of_pages = 0
        self.max_files = 512
        self.request_GET = var_parse(request.query)

        self._parse_filepath_and_name()
        self.is_dir = self._is_dir()
        self.page = self._paginated()

        self.return_raw = self._return_raw()
        self.folder = None

        self.file_path_quoted = quote_plus(self.file_path)

    def get_raw_output(self, format):
        if format == 'json':
            pass
        elif format == 'plain':
            data = []

            for source_file in self.folder.source_files:
                if source_file.filename_human == '..':
                    continue

                data.append('[%s] %s%s%s' % (
                    'D' if source_file.is_directory else 'F',
                    self.folder.source.crawl_url,
                    source_file.filepath_human,
                    source_file.filename_human))

            return '\n'.join(data)

    def get_files(self):
        page = self._paginated()

        if self.number_of_pages != 0:
            source_files = self.folder.source_files

            if page > self.number_of_pages:
                return
            elif page == 1:
                return source_files[:self.max_files]
            else:
                return source_files[(page-1)*self.max_files:][:self.max_files]
        else:
            return self.folder.source_files

    def _calculate_number_of_pages(self):
        if len(self.folder.source_files) > self.max_files:
            source_files = self.folder.source_files
            self.number_of_pages = int(math.ceil(float(len(source_files)) / float(self.max_files)))

    def _calculate_folder_size(self):
        for source_file in self.folder.source_files:
            e = ''

    def _paginated(self):
        if 'page' in self.request_GET:
            try:
                return int(self.request_GET['page'][0])
            except:
                return 1
        return 1

    def _is_dir(self):
        if self.request_path.endswith('/'):
            return True

    def _parse_filepath_and_name(self):
        spl = self.request_path.split('/')
        self.source_name = spl[0]
        self.file_path = '/' + '/'.join(spl[1:-1])

        if not self._is_dir():
            self.file_name = self.request_path.split('/')[-1]
        if self.file_path != '/':
            self.file_path += '/'

    def _return_raw(self):
        if self.request.query_string.startswith('raw=') and len(self.request.query_string) >= 5:
            query_string = self.request.query_string[4:]
            if query_string == 'plain' or query_string == 'json' or query_string == 'xml':
                return query_string

    def set_folder(self, folder):
        self.folder = folder
        self._calculate_number_of_pages()


def var_parse(query):
    '''
        Parses 'GET' parameters from the requested URL; returns a dictionairy.

        Example:
            http://domain.org/browse?sort=[size=desc,country=nl,en]&filter=bla

        Would result in:
            {
                'sort': {
                    'size': 'desc',
                    'country': ['nl','en']
                },
                'filter': 'bla'
            }
    '''
    parsed = {}

    for key, val in query.iteritems():
        if val.startswith('[') and val.endswith(']'):
            val = val[1:-1]

            if ',' in val:
                val = [z for z in val.split(',') if z]
            else:
                val = [val] if val else None

            if val:
                newval = []

                for v in val:
                    if '=' in v:
                        spl = v.split('=')

                        if len(spl) == 2 and spl[0] and spl[1]:
                            try:
                                spl[1] = int(spl[1])
                            except:
                                pass

                            newval.append({spl[0]: spl[1]})

                            continue
                        else:
                            continue

                    newval.append(v)
                parsed[key] = newval
        else:
            parsed[key] = [val] if val else []

    return parsed