import flask

from findex_gui import app, themes
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
    if not parsed:
        return 'w0w debug diz'

    browse = Browse()

    if parsed['path'].endswith('/'):
        data = browse.browse(parsed)
        return themes.render('main/browse_dir', **data)
    else:
        return """
        The file browser has a 'src' link in the table.
        <a href="javascript:history.back()">Please click here</a> to go back.
        """


@app.route("/research")
def research():
    return themes.render('main/research')