import string
import ntpath

from flask import request, Response, make_response, stream_with_context
from flask_babel import gettext

# from findex_gui.controllers.relay.relay import ReverseProxyController
from findex_gui.controllers.relay.proxy import ReverseProxyController
from findex_gui.controllers.browse.browse import Browse
from findex_gui import app


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
        "exts": ["ogg", "mp4", "webm"],
    },
    "document": {
        "stream": False,
        "buffer_size": 750000,  # 1MB : 8 Mbps
        "max_backend_response": 120000,  # 120KB
        "exts": ["txt", "nfo", "ascii", "py",
                 "js", "css", "md", "html",
                 "htm", "conf", "cfg", "srt",
                 "sub", "sh", "pl", "php"],
    }
}


def get_relay_category_by_extension(ext):
    extension = {cat: v for cat, v in EXTENSIONS_AND_CONSTRAINTS.items() if ext in v["exts"]}
    if not extension:
        return {}
    return next(iter(extension.items()))


@app.route("/relay/<browse:parsed>")
def relay(parsed):
    """Relay a file - must be in `EXTENSIONS_AND_CONSTRAINTS`"""

    filename = ntpath.basename(parsed["path"])
    path = "%s/" % "/".join(parsed["path"].split("/")[:-1])

    try:
        f = Browse().get_file(resource_id=parsed["resource_id"],
                              file_name=filename,
                              file_path=path)
    except:
        return gettext("file not found"), 500

    # check if relaying is enabled
    if not f.resource.meta.relay_enabled:
        return gettext("error: relaying not enabled for this resource"), 500

    # file, not dir
    if f.file_isdir:
        return gettext("error: was directory; file needed"), 500

    # file is in the allowed extensions
    extension = get_relay_category_by_extension(f.file_ext)
    if not extension:
        return gettext("error: file not in allowed extensions"), 500
    ext_category, ext_properties = extension

    # @TODO: validate address
    if "://" not in f.path_direct:
        return gettext("malformed uri"), 500
    path_proto = f.path_direct[:f.path_direct.find("://")+3]

    # setup a connection to the resource
    response_backend = None

    # check if the direct URL supports "Range"-like headers
    if path_proto.startswith(("http://", "https://")):
        relay_proxy = {}
        _relay_proxy = f.resource.meta.relay_proxy
        if _relay_proxy:
            if not _relay_proxy.startswith("socks5://"):
                return gettext("only socks5:// proxies supported"
                            "for HTTP(s) backends (change the "
                            "relay_proxy for this resource)"), 500
            relay_proxy = {"http": _relay_proxy,
                           "https": _relay_proxy}

        response_backend = ReverseProxyController.http(
            f=f, headers_in=request.headers,
            socks5=relay_proxy, stream=ext_properties["stream"])

    if not response_backend:
        return gettext("backend protocol not supported"), 500

    # enforce max_backend_response constraint
    response_backend_content_length = response_backend.headers.get("Content-Length", 0)
    if not response_backend_content_length.isdigit() or \
                    int(response_backend_content_length) > ext_properties["max_backend_response"]:
        return gettext("file too big for relaying"), 500

    # enforce Content-Type header from response_backend
    if not response_backend.headers.get("Content-Type"):
        return gettext("response backend did not send Content-Type"), 500

    # make response to client
    stream = ext_properties["stream"]
    response_status = 206 if stream else 200

    response_bufsize = ext_properties["buffer_size"]

    if not ext_properties["stream"]:
        content = response_backend.content.decode("ascii", errors="ignore")
        content = [x for x in content if x in string.printable]
        content = content.replace("\r\n", "\n")
        content = "\n".join(content.split("\n")[:512])

        r = make_response(content, 200)
        r.headers.set("Content-Type", "text/plain; charset=UTF-8")
        r.headers.set("Content-Disposition", "inline;filename=%s" % filename)
        return r

    response = Response(
        response=stream_with_context(
            response_backend.iter_content(chunk_size=response_bufsize)),
        status=response_status,
        content_type=response_backend.headers["Content-Type"],
        direct_passthrough=False)

    # @TODO: leaks unnecessary backend response headers - use a whitelist of headers
    for header, val in response_backend.raw.headers.items():
        response.headers[header] = val
        print("added: " + header)
    response.headers['Cache-Control'] = 'no-cache'

    return response
