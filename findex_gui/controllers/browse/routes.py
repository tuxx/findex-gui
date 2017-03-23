import ntpath
import tarfile
from io import StringIO

from requests import get
from flask import Response, send_file, request
from flask_babel import gettext

import findex_gui.controllers.browse.converters
from findex_gui import app, themes, db
from findex_gui.controllers.browse.browse import Browse
from findex_gui.controllers.resources.resources import ResourceController
from findex_gui.controllers.relay.routes import get_relay_category_by_extension
from findex_common.static_variables import FileProtocols, ResourceStatus
from findex_common.utils_time import TimeMagic


@app.route("/browse")
def browse_home():
    #@TODO replace with API call @ frontend

    resources = ResourceController.get_resources()
    for r in resources:
        setattr(r, "protocol_human", FileProtocols().name_by_id(r.protocol))
        setattr(r, "ago", TimeMagic().ago_dt(r.date_crawl_end))
        setattr(r, "status_human", ResourceStatus().name_by_id(r.meta.status))

    resources = sorted(resources, key=lambda k: k.meta.file_count, reverse=True)
    return themes.render("main/browse", resources=resources)


@app.route("/browse/<browse:args>")
def browse(args):
    resource, path, filename = args

    browse = Browse()
    if path.endswith("/"):
        browser = browse.browse(resource, path, filename)
        return themes.render("main/browse_dir", browser=browser)
    else:
        filename = ntpath.basename(path)
        path = "%s/" % "/".join(path.split("/")[:-1])

        try:
            f = Browse().get_file(resource_id=resource.id,
                                  file_name=filename,
                                  file_path=path)
        except:
            return gettext("error")

        path = f.path_dir[len(resource.id):]
        browser = browse.browse(resource, path, filename)

        return themes.render("main/file_viewer/viewer", f=f, browser=browser,
                             get_relay_category_by_extension=get_relay_category_by_extension)


@app.route("/index_as_csv/<browse:args>/")
def index_as_csv(args):
    # @TODO: sequentially write response if possible
    resource, path, filename = args

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
