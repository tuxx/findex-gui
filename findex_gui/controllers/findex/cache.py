from findex_gui.db.orm import Resources


class CacheController():
    def __init__(self, db):
        self.db = db
        self.resources = {}

    def __getitem__(self, item):
        if item in self.resources:
            return self.resources[item]

    def all(self):
        resources = self.db.query(Resources).all()
        if resources:
            self.resources = {}
            for resource in resources:
                setattr(resource, 'identifier', '%s:%s' % (resource.address, int(resource.port)))
                self.resources[resource.id] = resource

    def loop(self):
        self.all()