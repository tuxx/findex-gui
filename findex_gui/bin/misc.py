# Code borrowed from 'Cuckoo Sandbox'
#   https://github.com/cuckoosandbox/cuckoo
# Credits go to @jbremer (Jurriaan Bremer) and the Cuckoo team

import os
import sys
import hashlib
import shutil
import logging
import pkg_resources

import findex_gui
from findex_common.exceptions import StartupError

log = logging.getLogger(__name__)

_root = None
_raw = None

try:
    import pwd
    HAVE_PWD = True
except ImportError:
    HAVE_PWD = False


version = pkg_resources.require("findex-gui")[0].version


def mkdir(*args):
    """Create a directory without throwing exceptions if it already exists."""
    dirpath = os.path.join(*args)
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)


def getuser():
    if HAVE_PWD:
        return pwd.getpwuid(os.getuid())[0]
    return ""


def set_cwd(path, raw=None):
    global _root, _raw
    _root = path
    _raw = raw


def cwd(*args, **kwargs):
    """Returns absolute path to this file in the Findex Working Directory or
    optionally - when private=True has been passed along - to our private
    Findex Working Directory which is not configurable."""
    if kwargs.get("private"):
        return os.path.join(findex_gui.__path__[0], "data-private", *args)
    elif kwargs.get("raw"):
        return _raw
    elif kwargs.get("root"):
        return _root
    elif kwargs:
        raise RuntimeError(
            "Invalid arguments provided to cwd(): %r %r" % (args, kwargs)
        )
    else:
        return os.path.join(_root, *args)


def decide_cwd(cwd=None, exists=False):
    """Decides and sets the CWD, optionally checks if it's a valid CWD."""
    if not cwd:
        cwd = os.environ.get("FINDEX_CWD")

    if not cwd:
        cwd = os.environ.get("FINDEX")

    if not cwd and os.path.exists(".cwd"):
        cwd = "."

    if not cwd:
        cwd = "~/.findex"

    dirpath = os.path.abspath(os.path.expanduser(cwd))
    if exists:
        if not os.path.exists(dirpath):
            raise StartupError(
                "Unable to start this Findex command as the provided CWD (%r) "
                "is not present!" % dirpath
            )

        if not os.path.exists(os.path.join(dirpath, ".cwd")):
            raise StartupError(
                "Unable to start this Findex command as the provided CWD (%r) "
                "is not a proper CWD!" % dirpath
            )

    set_cwd(dirpath, raw=cwd)
    return dirpath


def migrate_cwd():
    path_hashes = cwd("cwd", "hashes.txt", private=True)
    if not os.path.isfile(path_hashes):
        log.error("hashes.txt could not found at %s" % path_hashes)
        return

    log.warning(
        "This is the first time you're running Findex after updating your "
        "local version of Findex. We're going to update files in your CWD "
        "that require updating. Note that we'll first ensure that no custom "
        "patches have been applied by you before applying any modifications "
        "of our own."
    )

    hashes = {}
    for line in open(path_hashes, "rb"):
        if not line.strip():
            continue
        hash_, filename = line.split()
        hashes[filename] = hashes.get(filename, []) + [hash_]

    modified, outdated = [], []
    for filename, hashes in hashes.items():
        if not os.path.exists(cwd(filename)):
            outdated.append(filename)
            continue
        hash_ = hashlib.sha1(open(cwd(filename), "rb").read()).hexdigest()
        if hash_ not in hashes:
            modified.append(filename)
        if hash_ != hashes[-1]:
            outdated.append(filename)

    if modified:
        log.error(
            "One or more files in the CWD have been modified outside of "
            "regular Findex usage. Due to these changes Findex isn't able to "
            "automatically upgrade your setup."
        )

        for filename in sorted(modified):
            log.warning("Modified file: %s (=> %s)", filename, cwd(filename))

        log.error("Moving forward you have two options:")
        log.warning(
            "1) You make a backup of the affected files, remove their "
            "presence in the CWD (yes, actually 'rm -f' the file), and "
            "re-run Findex to automatically restore the new version of the "
            "file. Afterwards you'll be able to re-apply any changes as you "
            "like."
        )
        log.warning(
            "2) You revert back to the version of Findex you were on "
            "previously and accept that manual changes that have not been "
            "merged upstream require additional maintenance that you'll "
            "pick up at a later point in time."
        )

        sys.exit(1)

    for filename in outdated:
        log.debug("Upgraded %s", filename)
        shutil.copy(cwd("..", "data", filename, private=True), cwd(filename))

    log.info(
        "Automated migration of your CWD was successful! Continuing "
        "execution of Findex as expected."
    )
