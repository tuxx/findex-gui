import requests
from requests.exceptions import HTTPError


class ReverseProxyController:
    @staticmethod
    def http(f, headers_in, stream, socks5={}, user_agent="VLC/2.2.4 LibVLC/2.2.4"):
        """
        :param f: <type>
        :param headers_in: incoming request headers from the client
        :param user_agent: str
        :return:
        """
        headers_out = {}
        for k, v in headers_in.iteritems():
            headers_out[k] = v

        for pop in ["host", "referer", "connection"]:
            headers_out.pop(pop.capitalize(), None)
            headers_out.pop(pop.lower(), None)
        
        args = {
            "url": f.path_direct,
            "stream": stream,
            "headers": headers_out,
            "allow_redirects": False,
            "timeout": 4,
            "proxies": socks5,
            "verify": False
        }

        if not socks5:
            args.pop("proxies", None)

        try:
            response = requests.get(**args)
            response.raise_for_status()
        except Exception as ex:
            raise HTTPError(ex)
        return response

    def _fs(self, path):
        """ @TODO: Example for FS relaying"""
        import mimetypes
        from flask import request, send_file, Response
        import os, re

        range_header = request.headers.get_url('Range', None)
        if not range_header: return send_file(path)

        size = os.path.getsize(path)
        byte1, byte2 = 0, None

        m = re.search('(\d+)-(\d*)', range_header)
        g = m.groups()

        if g[0]: byte1 = int(g[0])
        if g[1]: byte2 = int(g[1])

        length = size - byte1
        if byte2 is not None:
            length = byte2 - byte1

        data = None
        with open(path, 'rb') as f:
            f.seek(byte1)
            data = f.read(6291456)

        rv = Response(data,
                      206,
                      mimetype=mimetypes.guess_type(path)[0],
                      direct_passthrough=True)
        rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(byte1, byte1 + length - 1, size))
        rv.headers.add('Cache-Control', 'no-cache')
        return rv