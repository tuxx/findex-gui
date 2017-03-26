import ftplib
from io import BytesIO
from urllib.parse import urlparse

import magic
import requests
from requests.exceptions import HTTPError

from flask import request, Response, stream_with_context
from flask_babel import gettext

from findex_common.static_variables import FileProtocols
from findex_common.exceptions import RelayException


# @TODO: move constants to db so they can be changed from the user control panel
EXTENSIONS_AND_CONSTRAINTS = {
    "music": {
        "stream": True,
        "buffer_size": "750000",  # 1MB : 8 Mbps
        "max_backend_response": 1073741824,  # 1GB
        "exts": ["wav", "mp3"],
    },
    "video": {
        "stream": True,
        "buffer_size": 6291456,  # 6MB : 48 Mbps
        "max_backend_response": 59055800320,  # 55GB
        "exts": ["ogg", "mp4", "webm", "mkv"],
    },
    "document": {
        "stream": False,
        "buffer_size": 750000,  # 1MB
        "max_backend_response": 120000,  # 120KB
        "exts": ["txt", "nfo", "ascii", "py",
                 "js", "css", "md", "html",
                 "htm", "conf", "cfg", "srt",
                 "sub", "sh", "pl", "php"],
    },
    "picture": {
        "stream": False,
        "buffer_size": 750000*2,  # 2MB,
        "max_backend_response": 750000*2,
        "exts": [
            "jpg", "png", "jpeg", "svg", "gif"
        ]
    }
}


class StopIter(Exception): pass


class ReverseRelayController(object):
    """
    Relays a file from the remote resource, returns
    Flask.response. Either whole file is fetched and
    returned, or streamed (HTTP 206 - Partial Content)

    1) Call class with resource object/file object
    2) Check if relaying feature is enabled
    3) Determine the back-end relay protocol; `resources.display_url`
    has priority, else resource protocol is used
    4) Take note of incoming HTTP Range header
    5) Receive backend response - set appropriate headers and mimetypes
    5) Configure a Flask response object
    6) @TODO: update `Files` object mimetype
    """
    def __init__(self, resource, f, path, filename):
        if not resource.meta.relay_enabled:
            raise RelayException("Relay feature disabled for this resource")

        self.resource = resource
        self.file = f
        self.path = path
        self.filename = filename

        if self.file.file_isdir:
            RelayException("File needed, not directory")

        try:
            self.url_parsed = urlparse(self.file.path_direct)
        except:
            raise RelayException("could not urlparse `files.path_direct`")

        self.ext_category, self.ext_properties = self.get_relay_category(self.file.file_ext)

        if not self.file.path_direct:
            raise RelayException("path_direct error")

    def fetch(self):
        """fetch remote file, return Flask response"""
        offset = self._get_offset()

        # returns BytesIO, bytes or requests.models.Response
        rtn = self._fetch(offset=offset)
        if not rtn:
            raise RelayException("empty buffer received")

        mimetype = None
        buffer = None
        response_headers = {}
        length = 0

        if isinstance(rtn, requests.models.Response):
            mimetype = rtn.headers.get("content-type")
            buffer = rtn.iter_content

            for header, val in rtn.headers.items():  # @TODO: leaks backend response headers
                response_headers[header] = val

            if self.ext_properties["stream"]:
                buffer = stream_with_context(buffer(chunk_size=self.ext_properties["buffer_size"]))
            else:
                data = BytesIO()
                for _chunk in buffer(chunk_size=self.ext_properties["buffer_size"]):
                    data.write(_chunk)

                length = data.tell()
                buffer = data.getvalue()
                if not mimetype:
                    mimetype = magic.from_buffer(buffer[:1024], mime=True)

        elif isinstance(rtn, BytesIO):
            length = buffer.tell()
        elif isinstance(rtn, bytes):
            buffer = rtn
            length = len(buffer)
            mimetype = magic.from_buffer(buffer[:1024], mime=True)
        else:
            raise RelayException("unknown instance fetched")

        response = Response(
            response=buffer,
            status=206 if offset else 200,
            content_type=mimetype,
            direct_passthrough=False)

        response.headers["Cache-Control"] = "no-cache"
        for k, v in response_headers.items():
            response.headers[k] = v

        if self.ext_properties["stream"]:
            if not isinstance(rtn, requests.models.Response):
                response.headers["Content-Length"] = self.file.file_size if offset == 0 else length
                response.headers["Content-Range"] = "bytes {0}-{1}/{2}".format(
                    offset, (offset + length) - 1, self.file.file_size
                )

        return response

    @staticmethod
    def get_proto(f):
        """
        Returns the backend scheme needed
        to setup a direct connection as an
        integer (`findex_common.static_variables.FileProtocols`)
        :param f: `Files` orm instance
        :return: str
        """
        try:
            url_parsed = urlparse(f.path_direct)
        except:
            raise RelayException("could not urlparse `files.path_direct`")

        if url_parsed.scheme not in FileProtocols().data.keys():
            raise RelayException("protocol not implemented: %s" % url_parsed.scheme)

        return url_parsed.scheme

    def _fetch(self, offset):
        """
        Can return the following:
        1) bytes
        2) BytesIO
        3) requests.models.Response
        """
        pass

    @staticmethod
    def get_relay_category(ext):
        global EXTENSIONS_AND_CONSTRAINTS
        extension = {cat: v for cat, v in EXTENSIONS_AND_CONSTRAINTS.items() if ext in v["exts"]}
        if not extension:
            Exception("file not in allowed extensions")
        return next(iter(extension.items()))

    @staticmethod
    def _get_offset():
        """Parses incoming HTTP range header"""
        offset = request.headers.get("Range", 0)
        if offset:
            try:
                offset = int(offset.split("-")[0][6:])
            except ValueError:
                raise ValueError("could not parse incoming Range header")
        return offset


class ReverseHttpRelay(ReverseRelayController):
    def __init__(self, resource, f, path, filename):
        super(ReverseHttpRelay, self).__init__(resource, f, path, filename)

    def _fetch(self, offset=0):
        socks5 = {}
        _relay_proxy = self.resource.meta.relay_proxy
        if _relay_proxy:
            if not _relay_proxy.startswith("socks5://"):
                return gettext("only socks5:// proxies supported"
                               "for HTTP(s) backends (change the "
                               "relay_proxy for this resource)"), 500
            socks5 = {"http": _relay_proxy,
                      "https": _relay_proxy}

        request_headers = {}
        for k, v in request.headers.items():
            request_headers[k] = v

        for pop in ["host", "referer", "connection"]:
            request_headers.pop(pop.capitalize(), None)
            request_headers.pop(pop.lower(), None)

        request_args = {
            "url": self.file.path_direct,
            "stream": True,
            "headers": request_headers,
            "allow_redirects": False,
            "timeout": 4,
            "proxies": socks5,
            "verify": False
        }

        if not socks5:
            request_args.pop("proxies", None)

        try:
            response = requests.get(**request_args)
            response.raise_for_status()
        except Exception as ex:
            raise HTTPError(ex)

        # enforce max_backend_response constraint
        backend_length = response.headers.get("Content-Length", 0)
        if not backend_length.isdigit() or \
                        int(backend_length) > self.ext_properties["max_backend_response"]:
            return RelayException("file too big for relaying")

        # enforce Content-Type header from response_backend
        if not response.headers.get("Content-Type"):
            return RelayException("response backend did not send Content-Type")

        return response


class ReverseFtpRelay(ReverseRelayController):
    def __init__(self, resource, f, path, filename):
        super(ReverseFtpRelay, self).__init__(resource, f, path, filename)

    def _fetch(self, offset=0):
        port = self.url_parsed.port
        if not port:
            port = 21

        auth_user = self.resource.meta.get("auth_user", "anonymous")
        auth_pass = self.resource.meta.get("auth_pass", "anonymous")
        chunk_size = self.ext_properties["buffer_size"]
        data = BytesIO()

        ftp = ftplib.FTP()
        ftp.connect(self.url_parsed.hostname, port)
        ftp.login(auth_user, auth_pass)

        filepath = self.file.resource.basepath + self.file.file_path + self.filename

        def cb(_data):
            data.write(_data)
            if len(data.getvalue()) >= chunk_size:
                raise StopIter(None)  # hack to stop fetching after the first chunk is received
        try:
            ftp.retrbinary("RETR %s" % filepath, cb, blocksize=chunk_size, rest=offset)
        except StopIter as ex:
            pass

        data = data.getvalue()
        data = data[:chunk_size]
        return data


class ReverseFsRelay(ReverseRelayController):
    def __init__(self, resource, f, path, filename):
        super(ReverseFsRelay, self).__init__(resource, f, path, filename)

    def _fetch(self, offset=0):
        """ @TODO: Example for FS relaying"""
        pass
        # range_header = request.headers.get_url("Range", None)
        # if not range_header: return send_file(path)
        #
        # size = os.path.getsize(path)
        # byte1, byte2 = 0, None
        #
        # m = re.search("(\d+)-(\d*)", range_header)
        # g = m.groups()
        #
        # if g[0]: byte1 = int(g[0])
        # if g[1]: byte2 = int(g[1])
        #
        # length = size - byte1
        # if byte2 is not None:
        #     length = byte2 - byte1
        #
        # data = None
        # with open(path, "rb") as f:
        #     f.seek(byte1)
        #     data = f.read(6291456)
        #
        # rv = Response(data,
        #               206,
        #               mimetype=mimetypes.guess_type(path)[0],
        #               direct_passthrough=True)
        # rv.headers.add("Content-Range", "bytes {0}-{1}/{2}".format(byte1, byte1 + length - 1, size))
        # rv.headers.add("Cache-Control", "no-cache")
        # return rv
