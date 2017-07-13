import ntpath
import tarfile
from io import StringIO

from requests import get
from flask import Response, send_file, request
from flask_babel import gettext

import findex_gui.controllers.browse.converters
from findex_gui.web import app, themes, db
from findex_gui.orm.models import MetaImdb
from findex_gui.controllers.browse.browse import Browse
from findex_gui.controllers.resources.resources import ResourceController
from findex_gui.controllers.relay.relay import ReverseRelayController
from findex_common.static_variables import FileProtocols, ResourceStatus
from findex_common.utils_time import TimeMagic


@app.route("/test")
def test_dyna():
    return themes.render("main/test")


@app.route("/browse")
def browse_home():
    resources = ResourceController.get_resources()
    resources = sorted(resources, key=lambda k: k.meta.file_count, reverse=True)
    return themes.render("main/browse", resources=resources)


@app.route("/browse/<browse:args>")
def browse(args):
    resource, f, path, filename = args

    browse = Browse()
    if not filename:
        browser = browse.browse(resource, path, filename)
        return themes.render("main/browse_dir", browser=browser)

    browser = browse.browse(resource, path, "")

    imdb = None
    if f.meta_imdb:
        imdb = db.session.query(MetaImdb).filter(MetaImdb.id == f.meta_imdb).first()

    return themes.render("main/file_viewer/viewer",
                         f=f, browser=browser,
                         resource=resource,
                         imdb=imdb,
                         get_relay_category_by_extension=ReverseRelayController.get_relay_category)


@app.route("/index_as_csv/<browse:args>/")
def index_as_csv(args):
    # @TODO: sequentially write response if possible
    resource, f, path, filename = args

    plain = StringIO()
    plain.write("path,dir,size\n")
    compressed = StringIO()
    res = db.engine.execute("""
        SELECT
            concat(r.basepath,
                   files.file_path,
                   files.file_name,',',
                   files.file_isdir,',',
                   files.file_size)
        FROM files
        INNER JOIN resources r ON files.resource_id=r.id
        INNER JOIN server s ON r.server_id = s.id WHERE r.id=%d;
    """ % resource.id)
    if not res or isinstance(res, Exception):
        return "no results", 500
    for row in res:
        plain.write("%s\n" % row[0].encode("utf8"))

    plain.seek(0)
    tar = tarfile.open(fileobj=compressed, mode="w|gz")

    info = tar.tarinfo()
    info.name = "%s:%d.csv" % (resource.server.address, resource.port)
    info.uname = "findex"
    info.gname = "findex"
    info.size = plain.len

    tar.addfile(info, plain)
    tar.close()

    compressed.seek(0)
    return send_file(compressed, as_attachment=True, attachment_filename="%s:%d.tar.gz" % (
        resource.server.address,
        resource.port))


@app.route("/research")
def research():
    return themes.render("main/research")
