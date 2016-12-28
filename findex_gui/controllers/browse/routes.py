from flask import Response, send_file
import tarfile
import io
import sys
from StringIO import StringIO

from findex_gui import app, themes, db
import findex_gui.controllers.browse.converters
from findex_gui.controllers.browse.browse import Browse
from findex_gui.controllers.resources.resources import ResourceController
from findex_common.static_variables import FileProtocols, ResourceStatus
from findex_common.utils_time import TimeMagic

@app.route('/browse')
def browse_home():
    #@TODO replace with API call @ frontend
    from datetime import datetime

    resources = ResourceController.get_resources()
    for r in resources:
        setattr(r, "protocol_human", FileProtocols().name_by_id(r.protocol))
        setattr(r, "ago", TimeMagic().ago_dt(r.date_crawl_end))
        setattr(r, "status_human", ResourceStatus().name_by_id(r.meta.status))

    resources = sorted(resources, key=lambda r: r.meta.file_count, reverse=True)
    return themes.render('main/browse', resources=resources)


@app.route('/browse/<browse:parsed>')
def browse(parsed):
    if isinstance(parsed, Exception):
        return str(parsed)
    browse = Browse()
    if parsed['path'].endswith('/'):
        data = browse.browse(parsed)
        return themes.render('main/browse_dir', **data)
    else:
        return """
        The file browser has a 'src' link in the table.
        <a href="javascript:history.back()">Please click here</a> to go back.
        """


@app.route('/index_as_csv/<browse:parsed>/')
def index_as_csv(parsed):
    resource = Browse().get_resource(resource_id=parsed["resource_id"])

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
        return 'no results', 500
    for row in res:
        plain.write("%s\n" % row[0].encode("utf8"))

    plain.seek(0)
    tar = tarfile.open(fileobj=compressed, mode='w|gz')

    info = tar.tarinfo()
    info.name = '%s:%d.csv' % (resource.server.address, resource.port)
    info.uname = 'findex'
    info.gname = 'findex'
    info.size = plain.len

    tar.addfile(info, plain)
    tar.close()

    compressed.seek(0)
    return send_file(compressed, as_attachment=True, attachment_filename='%s:%d.tar.gz' % (
        resource.server.address,
        resource.port))


@app.route("/research")
def research():
    return themes.render('main/research')
