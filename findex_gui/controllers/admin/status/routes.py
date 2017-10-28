from findex_gui.web import app, themes
from findex_gui.controllers.admin.status.status import AdminStatusController
from findex_gui.controllers.user.decorators import admin_required


@app.route("/admin/status/overview")
@admin_required
def admin_status_overview():
    results = AdminStatusController.overview()
    return themes.render("main/status/overview", theme="_admin", results=results)


@app.route("/admin/status/findex")
@admin_required
def admin_status_findex():
    results = AdminStatusController.findex()
    return themes.render("main/status/items", theme="_admin", name="findex", data=results)


@app.route("/admin/status/database")
@admin_required
def admin_status_database():
    results = AdminStatusController.database()
    return themes.render("main/status/items", theme="_admin", name="database", data=results)


@app.route("/admin/status/system")
@admin_required
def admin_status_system():
    results = AdminStatusController.system()
    return themes.render("main/status/items", theme="_admin", name="system", data=results)


@app.route("/admin/status/python")
@admin_required
def admin_status_pip():
    results = AdminStatusController.pip()
    return themes.render("main/status/items", theme="_admin", name="python", data=results)
