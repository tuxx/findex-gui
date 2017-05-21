from findex_gui.controllers.relay.relay import (
    ReverseRelayController, ReverseHttpRelay, ReverseFtpRelay, ReverseFsRelay, RelayException)
from findex_gui.web import app


@app.route("/relay/<browse:args>")
def relay(args):
    """Relay a file"""
    resource, f, path, filename = args
    if not f:
        raise RelayException("file not found")

    proto = ReverseRelayController.get_proto(f)
    if proto in ("http", "https"):  # http, https
        relay = ReverseHttpRelay(*args)
    elif proto in ("ftp", "ftps"):  # ftp, ftps
        relay = ReverseFtpRelay(*args)
    elif proto in ("fs"):  # filesystem
        relay = ReverseFsRelay(*args)
    else:
        raise RelayException("protocol not implemented")

    response = relay.fetch()
    return response
