# Code borrowed from 'Cuckoo Sandbox'
#   https://github.com/cuckoosandbox/cuckoo
# Credits go to @jbremer (Jurriaan Bremer) and the Cuckoo team

import os

from findex_common.exceptions import StartupError
from findex_gui.bin.misc import cwd
from findex_gui.bin.config import Config, config
from findex_common.colors import green, red


def check_specific_config(filename):
    sections = Config.configuration[filename]
    for section, entries in sections.items():
        if section == "*" or section == "__star__":
            continue

        # If an enabled field is present, check it beforehand.
        if config("%s:%s:enabled" % (filename, section)) is False:
            continue

        for key, value in entries.items():
            config(
                "%s:%s:%s" % (filename, section, key),
                check=True, strict=True
            )


def check_configs():
    """Checks if config files exist.
    @raise StartupError: if config files do not exist.
    """
    configs = (
        "findex",
    )

    for filename in configs:
        if not os.path.exists(cwd("conf", "%s.conf" % filename)):
            raise StartupError(
                "Config file does not exist at path: %s" %
                cwd("conf", "%s.conf" % filename)
            )

        check_specific_config(filename)
    return True


def check_version():
    """Checks version of Findex."""
    #print(green(" You're good to go!"))
    return
