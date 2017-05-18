from sqlalchemy import event, DDL

from findex_gui.bin.config import config
from findex_gui.web import db
from findex_gui.orm.models import Files

#@TODO: move this to package sqlalchemy_zdb

# Creates a composite type for the `files` table, to be
# used during zombodb partial index creation. executes
# regardless of `settings.es_enabled`.
event.listen(
    Files.__table__,
    "before_create",
    DDL("""
        CREATE TYPE type_files AS (%s);
        """ % Files.get_columns_as_ddl(zombodb_only=True)
    ).execute_if(
        callable_=lambda *args, **kwargs: not db.check_type("type_files")
    )
)

# Creates the partial index used by zombodb. Can
# take a while to finish. Only executes when
# `settings.es_enabled` is set to True
event.listen(
    Files.__table__,
    "after_create",
    DDL("""
        CREATE INDEX idx_zdb_files ON files
        USING zombodb(
            zdb('files', ctid),
            zdb(ROW(%s)::type_files))
        WITH (url='%s');
    """ % (", ".join([column.name for column in Files.get_columns(zombodb_only=True)]),
           config("findex:elasticsearch:host"))
    ).execute_if(
        callable_=lambda *args, **kwargs: not db.check_index(table_name="files", index="idx_zdb_files") and config("findex:elasticsearch:enabled")
    )
)
