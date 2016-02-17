import os, appdirs, ConfigParser, inspect

from findex_common.exceptions import ConfigError


class FindexGuiConfig():
    def __init__(self):
        self.items = {}
        self.path = os.path.join(appdirs.user_config_dir('findex'), 'gui.cfg')
        self.config = ConfigParser.ConfigParser()

        if not os.path.isfile(self.path):
            try:
                os.mkdir(os.path.dirname(self.path))
            except:
                pass

    # to-do: ?
    def __getitem__(self, key):
        if not key in self.items:
            #raise ConfigError('Required block \'%s\' not found in config file \'%s\'.' % (key, self.path))
            self.items[key] = {}

        return self.items[key]

    def setitem(self, section, key, val):
        if not section in self.items:
            self.items[section] = {}

        self.items[section][key] = val

    def load(self):
        self.config.read(self.path)

        data = {}
        for section in self.config.sections():
            data[section] = {}

            for k, v in self.config.items(section):
                if k.startswith('#') or v.startswith('#'):
                    continue

                if v:
                    try:
                        data[section][k] = int(v) if not '.' in v else float(v)
                        continue
                    except:
                        pass

                    if v.lower() == 'false':
                        data[section][k] = False
                        continue
                    elif v.lower() == 'true':
                        data[section][k] = True
                        continue

                data[section][k] = v

        self.items = data

    def get(self, section, item):
        try:
            return self.items[section][item]
        except:
            frm = inspect.stack()[1]
            mod = inspect.getmodule(frm[0])
            raise ConfigError('Could not access config variable \'%s\' from section \'%s\' - Caller: %s' % (item, section, mod.__name__))

    def write(self):
        self.config = ConfigParser.ConfigParser()
        f = open(self.path, 'w')

        for k, v in self.items.iteritems():
            self.config.add_section(k)

            for x, y in v.iteritems():
                self.config.set(k, x, y)

        self.config.write(f)
        f.close()

        self.load()