# Code borrowed from 'Cuckoo Sandbox'
#   https://github.com/cuckoosandbox/cuckoo
# Credits go to @jbremer (Jurriaan Bremer) and the Cuckoo team

import binascii
import configparser as ConfigParser
import click
import os
import logging
import re

from findex_common.exceptions import ConfigError
from findex_gui.bin.misc import cwd

log = logging.getLogger(__name__)
basestring = (str, bytes)

_cache = {}


def parse_bool(value):
    """Attempt to parse a boolean value."""
    if value in ("true", "True", "yes", "1", "on"):
        return True
    if value in ("false", "False", "None", "no", "0", "off"):
        return False
    return bool(int(value))


class Dictionary(dict):
    """Cuckoo custom dict."""

    def __getattr__(self, key):
        return self.get(key, None)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Type(object):
    """Base Class for Type Definitions"""

    def __init__(self, default=None, required=True, sanitize=False,
                 allow_empty=False):
        self.required = required
        self.sanitize = sanitize
        self.allow_empty = allow_empty
        self.default = self.parse(default)

    def parse(self, value):
        """Parse a raw input value."""

    def check(self, value):
        """Checks the type of the value."""

    def emit(self, value):
        """String-readable version of this object"""


class Int(Type):
    """Integer Type Definition class."""

    def parse(self, value):
        if isinstance(value, int):
            return value

        if isinstance(value, basestring) and value.isdigit():
            return int(value)

    def check(self, value):
        if self.allow_empty and not value:
            return True

        try:
            click.INT(value)
            return True
        except:
            return False

    def emit(self, value):
        return "%d" % value if value is not None else ""


class String(Type):
    """String Type Definition class."""

    def parse(self, value):
        return value.strip() if value else None

    def check(self, value):
        if self.allow_empty and not value:
            return True

        return isinstance(value, basestring)

    def emit(self, value):
        return value or ""


class Path(String):
    """Path Type Definition class."""

    def __init__(self, default=None, exists=False, writable=False,
                 readable=False, required=True, allow_empty=False,
                 sanitize=False):
        self.exists = exists
        self.writable = writable
        self.readable = readable
        super(Path, self).__init__(default, required, sanitize, allow_empty)

    def parse(self, value):
        if self.allow_empty and not value:
            return

        try:
            c = click.Path(
                exists=self.exists,
                writable=self.writable,
                readable=self.readable
            )
            return c.convert(value, None, None)
        except Exception:
            return value

    def check(self, value):
        if self.allow_empty and not value:
            return True

        try:
            c = click.Path(
                exists=self.exists,
                writable=self.writable,
                readable=self.readable
            )
            c.convert(value, None, None)
            return True
        except:
            return False

    def emit(self, value):
        return value or ""


class Boolean(Type):
    """Boolean Type Definition class."""

    def parse(self, value):
        try:
            return parse_bool(value)
        except:
            log.error("Incorrect Boolean %s", value)

    def check(self, value):
        try:
            parse_bool(value)
            return True
        except:
            return False

    def emit(self, value):
        return "yes" if value else "no"


class UUID(Type):
    """UUID Type Definition class."""

    def parse(self, value):
        try:
            c = click.UUID(value)
            return str(c)
        except:
            log.error("Incorrect UUID %s", value)

    def check(self, value):
        """Checks if the value is of type UUID."""
        try:
            click.UUID(value)
            return True
        except:
            return False

    def emit(self, value):
        return value


class List(Type):
    """List Type Definition class."""

    def __init__(self, subclass, default, sep=",", strip=True):
        self.subclass = subclass
        self.sep = sep
        self.strip = strip
        super(List, self).__init__(default)

    def parse(self, value):
        if value is None:
            return []

        try:
            ret = []

            if isinstance(value, (tuple, list)):
                for entry in value:
                    ret.append(self.subclass().parse(entry))
                return ret

            for entry in re.split("[%s]" % self.sep, value):
                if self.strip:
                    entry = entry.strip()
                    if not entry:
                        continue

                ret.append(self.subclass().parse(entry))
            return ret
        except:
            log.error("Incorrect list: %s", value)

    def check(self, value):
        try:
            value.split(self.sep)
            return True
        except:
            return False

    def emit(self, value):
        return (", " if self.sep[0] == "," else self.sep[0]).join(value or "")


class Config(object):
    """Configuration file parser."""

    configuration = {
        "findex": {
            "findex": {
                "application_root": String("/"),
                "secret_token": String(binascii.hexlify(open("/dev/urandom", "rb").read(32)).decode("UTF-8")),
                "version_check": Boolean(False),
                "debug": Boolean(False),
                "async": Boolean(True),
            },
            "database": {
                "connection": String(sanitize=True),
                "debug": Boolean(False),
            },
            "elasticsearch": {
                "enabled": Boolean(True),
                "host": String("http://localhost:9200/")
            },
            "rabbitmq": {
                "host": String(""),
                "username": String("changeme"),
                "password": String("changeme"),
                "virtual_host": String(""),
                "queue_name": String(""),
                "queue_size": Int(20)
            },
            "users": {
                "default_root_password": String("changeme"),
                "default_anon_password": String("changeme")
            }
        }
    }

    def get_section_types(self, file_name, section, strict=False, loose=False):
        """Get types for a section entry."""
        section_types = get_section_types(file_name, section)
        if not section_types and not loose:
            log.error(
                "Config section %s:%s not found!", file_name, section
            )
            if strict:
                raise ConfigError(
                    "Config section %s:%s not found!", file_name, section
                )
            return
        return section_types

    def __init__(self, file_name="findex", cfg=None, strict=False,
                 loose=False, raw=False):
        """
        @param file_name: file name without extension.
        @param cfg: configuration file path.
        """
        env = {}
        for key, value in os.environ.items():
            if key.startswith("CUCKOO_"):
                env[key] = value

        env["FINDEX_CWD"] = cwd()
        env["FINDEX_APP"] = os.environ.get("FINDEX_APP", "")
        config = ConfigParser.ConfigParser(env)

        self.env_keys = []
        for key in env.keys():
            self.env_keys.append(key.lower())

        self.sections = {}

        try:
            config.read(cfg or cwd("conf", "%s.conf" % file_name))
        except ConfigParser.ParsingError as e:
            raise ConfigError(
                "There was an error reading in the $CWD/conf/%s.conf "
                "configuration file. Most likely there are leading "
                "whitespaces in front of one of the key=value lines defined. "
                "More information from the original exception: %s" %
                (file_name, e)
            )

        if file_name not in self.configuration and not loose:
            log.error("Unknown config file %s.conf", file_name)
            return

        for section in config.sections():
            types = self.get_section_types(file_name, section, strict, loose)
            if types is None:
                continue

            self.sections[section] = Dictionary()
            setattr(self, section, self.sections[section])

            try:
                items = config.items(section)
            except ConfigParser.InterpolationMissingOptionError as e:
                log.error("Missing environment variable(s): %s", e)
                raise ConfigError(
                    "Missing environment variable: %s" % e
                )

            for name, raw_value in items:
                if name in self.env_keys:
                    continue

                if "\n" in raw_value:
                    wrong_key = "???"
                    try:
                        wrong_key = raw_value.split("\n", 1)[1].split()[0]
                    except:
                        pass

                    raise ConfigError(
                        "There was an error reading in the $CWD/conf/%s.conf "
                        "configuration file. Namely, there are one or more "
                        "leading whitespaces before the definition of the "
                        "'%s' key/value pair in the '%s' section. Please "
                        "remove those leading whitespaces as Python's default "
                        "configuration parser is unable to handle those "
                        "properly." % (file_name, wrong_key, section)
                    )

                if not raw and name in types:
                    # TODO Is this the area where we should be checking the
                    # configuration values?
                    # if not types[name].check(raw_value):
                    #     print file_name, section, name, raw_value
                    #     raise

                    value = types[name].parse(raw_value)
                else:
                    if not loose:
                        log.error(
                            "Type of config parameter %s:%s:%s not found! "
                            "This may indicate that you've incorrectly filled "
                            "out the Cuckoo configuration, please double "
                            "check it.", file_name, section, name
                        )
                    value = raw_value

                self.sections[section][name] = value

    def get(self, section):
        """Get option.
        @param section: section to fetch.
        @raise ConfigError: if section not found.
        @return: option value.
        """
        if section not in self.sections:
            raise ConfigError(
                "Option %s is not found in configuration" % section
            )

        return self.sections[section]

    @staticmethod
    def from_confdir(dirpath, loose=False, sanitize=False):
        """Reads all the configuration from a configuration directory. If
        `sanitize` is set, then black out sensitive fields."""
        ret = {}
        for filename in os.listdir(dirpath):
            if not filename.endswith(".conf"):
                continue

            config_name = filename.rsplit(".", 1)[0]
            cfg = Config(
                config_name, cfg=os.path.join(dirpath, filename), loose=loose
            )

            ret[config_name] = {}
            for section, values in cfg.sections.items():
                ret[config_name][section] = {}
                types = cfg.get_section_types(
                    config_name, section, loose=loose
                ) or {}
                for key, value in values.items():
                    if sanitize and key in types and types[key].sanitize:
                        value = "*"*8

                    ret[config_name][section][key] = value
        return ret


def parse_options(options):
    """Parse the analysis options field to a dictionary."""
    ret = {}
    for field in options.split(","):
        if "=" not in field:
            continue

        key, value = field.split("=", 1)
        ret[key.strip()] = value.strip()
    return ret


def emit_options(options):
    """Emit the analysis options from a dictionary to a string."""
    return ",".join("%s=%s" % (k, v) for k, v in sorted(options.items()))


def config(s, cfg=None, strict=False, raw=False, loose=False, check=False):
    """Fetch a configuration value, denoted as file:section:key."""
    if s.count(":") != 2:
        raise RuntimeError("Invalid configuration entry: %s" % s)

    file_name, section, key = s.split(":")

    if check:
        strict = raw = loose = True

    type_ = Config.configuration.get(file_name, {}).get(section, {}).get(key)
    if strict and type_ is None:
        raise ConfigError(
            "No such configuration value exists: %s" % s
        )

    required = type_ is not None and type_.required
    index = file_name, cfg, cwd(), strict, raw, loose

    if index not in _cache:
        _cache[index] = Config(
            file_name, cfg=cfg, strict=strict, raw=raw, loose=loose
        )

    config = _cache[index]

    if strict and required and section not in config.sections:
        raise ConfigError(
            "Configuration value %s not present! This may indicate that "
            "you've incorrectly filled out the Cuckoo configuration, "
            "please double check it." % s
        )

    section = config.sections.get(section, {})
    if strict and required and key not in section:
        raise ConfigError(
            "Configuration value %s not present! This may indicate that "
            "you've incorrectly filled out the Cuckoo configuration, "
            "please double check it." % s
        )

    value = section.get(key, type_.default if type_ else None)

    if check and not type_.check(value):
        raise ConfigError(
            "The configuration value %r found for %s is invalid. Please "
            "update your configuration!" % (value, s)
        )

    return value


def get_section_types(file_name, section, strict=False):
    if section in Config.configuration.get(file_name, {}):
        return Config.configuration[file_name][section]

    if "__star__" not in Config.configuration.get(file_name, {}):
        return {}

    if strict:
        section_, key = Config.configuration[file_name]["__star__"]
        if section not in config("%s:%s:%s" % (file_name, section_, key)):
            return {}

    if "*" in Config.configuration.get(file_name, {}):
        section_types = Config.configuration[file_name]["*"]
        # If multiple default values have been provided, pick one.
        if isinstance(section_types, (tuple, list)):
            section_types = section_types[0]
        return section_types
    return {}


def config2(file_name, section):
    keys = get_section_types(file_name, section, strict=True)
    if not keys:
        raise ConfigError(
            "No such configuration section exists: %s:%s" %
            (file_name, section)
        )

    ret = Dictionary()
    for key in keys:
        if key == "__star__" or key == "*":
            continue
        ret[key] = config("%s:%s:%s" % (file_name, section, key))
    return ret


def cast(s, value):
    """Cast a configuration value as per its type."""
    if s.count(":") != 2:
        raise RuntimeError("Invalid configuration entry: %s" % s)

    file_name, section, key = s.split(":")
    type_ = get_section_types(file_name, section).get(key)
    if type_ is None:
        raise ConfigError(
            "No such configuration value exists: %s" % s
        )

    return type_.parse(value)


def read_kv_conf(filepath):
    """Reads a flat Findex key/value configuration file."""
    ret = {}
    for line in open(filepath, "r"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            raise ConfigError(
                "Invalid flat configuration line: %s (missing '=' character)" %
                line
            )

        key, raw_value = line.split("=", 1)
        key, raw_value = key.replace(".", ":").strip(), raw_value.strip()
        try:
            value = cast(key, raw_value)
        except (ConfigError, RuntimeError) as e:
            raise ConfigError(
                "Invalid flat configuration line: %s (error %s)" % (line, e)
            )

        if raw_value and value is None:
            raise ConfigError(
                "Invalid flat configuration entry: %s is None" % key
            )

        a, b, c = key.split(":")
        ret[a] = ret.get(a, {})
        ret[a][b] = ret[a].get(b, {})
        ret[a][b][c] = value
    return ret


def generate_crawl_config(bot_name: str,
                          db_host: str,
                          db_port: int,
                          db_name: str,
                          db_user: str,
                          db_pass: str,
                          db_max_bulk_inserts: int,
                          amqp_username: str,
                          amqp_password: str,
                          amqp_host: str,
                          amqp_vhost: str,
                          amqp_queue_name: str,
                          amqp_queue_size: str):
    from jinja2 import Environment
    from findex_gui.bin.misc import cwd
    f = open(cwd("conf/crawl.conf"), "r")
    template = f.read()
    f.close()

    rendered = Environment().from_string(template).render(
        bot_name=bot_name,
        db_host=db_host,
        db_port=db_port,
        db_db=db_name,
        db_user=db_user,
        db_pass=db_pass,
        db_max_bulk_inserts=db_max_bulk_inserts,
        amqp_username=amqp_username,
        amqp_password=amqp_password,
        amqp_vhost=amqp_vhost,
        amqp_host=amqp_host,
        amqp_queue_name=amqp_queue_name,
        amqp_queue_size=amqp_queue_size
    )

    return rendered