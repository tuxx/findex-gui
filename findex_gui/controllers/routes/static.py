import os
from findex_gui.web import app
from findex_gui.bin.misc import cwd
from flask import render_template, request, flash, session, redirect, url_for, send_from_directory, abort


@app.route("/static/<path:filename>")
def static(filename):
    if filename.startswith("/"):
        return abort(404)

    from findex_gui.web import themes

    filename = filename.replace("..", "")
    filename = filename.replace("./", "")

    if filename.startswith("meta/posters/"):
        _cwd = cwd()
        filename = filename[13:]
        directory = "%s/meta/posters/" % _cwd
        if os.path.isfile("%s%s" % (directory, filename)):
            return send_from_directory(directory, filename)

    search_dirs = ["static/"]

    if filename.startswith("themes/"):
        spl = filename.split("/")

        if len(spl) >= 3 and spl[2] == "static":
            filename = "/".join(spl[3:])
            search_dirs.insert(0, "themes/%s/static/" % spl[1])

    for search_dir in search_dirs:
        directory = "%s/%s" % (app.config["dir_base"], search_dir)

        if os.path.isfile(directory + filename):
            return send_from_directory(directory, filename)

    return themes.render("errors/404", status_code=404)
