# Code borrowed from 'Cuckoo Sandbox' (https://github.com/cuckoosandbox/cuckoo)
# Credits go to @jbremer (Jurriaan Bremer) and the Cuckoo team

import click
import jinja2
import logging
import os
import shutil
import platform
import sys
import traceback

import findex_gui
from findex_gui.bin.misc import cwd, version, getuser, decide_cwd, migrate_cwd
from findex_gui.bin.startup import check_configs, check_version
from findex_gui.bin.config import Config, config
from findex_common.logo import logo
from findex_common.colors import yellow, red, green
from findex_common.exceptions import ConfigError, FindexException

log = logging.getLogger("findex")


def findex_create(username=None, cfg=None, quiet=False):
    """Create a new Findex Working Directory."""
    if not quiet:
        print(jinja2.Environment().from_string(
            open(cwd("cwd", "init-pre.jinja2", private=True), "r").read()
        ).render(cwd=cwd, yellow=yellow, red=red))

    if not os.path.isdir(cwd()):
        os.mkdir(cwd())

    def _ignore_pyc(src, names):
        """Don't copy .pyc files."""
        return [name for name in names if name.endswith(".pyc")]

    # The following effectively nops the first os.makedirs() call that
    # shutil.copytree() does as we've already created the destination
    # directory ourselves (assuming it didn't exist already).
    orig_makedirs = shutil.os.makedirs

    def _ignore_first_makedirs(dst):
        shutil.os.makedirs = orig_makedirs

    shutil.os.makedirs = _ignore_first_makedirs
    shutil.copytree(
        os.path.join(findex_gui.__path__[0], "data"),
        cwd(), symlinks=True, ignore=_ignore_pyc
    )

    # Drop our version of the CWD.
    our_version = open(cwd(".cwd", private=True), "r").read()
    open(cwd(".cwd"), "w").write(our_version)

    write_findex_conf(cfg=cfg)

    if not quiet:
        print("")
        print(jinja2.Environment().from_string(
            open(cwd("cwd", "init-post.jinja2", private=True), "r").read()
        ).render())


def findex_init(level, ctx, cfg=None):
    """Initialize Findex configuration.
    @param quiet: enable quiet mode.
    """
    logo(version)

    # It would appear this is the first time Findex is being run (on this
    # Findex Working Directory anyway).
    if not os.path.isdir(cwd()) or not os.listdir(cwd()):
        findex_create(cfg=cfg)
        sys.exit(0)

    # Determine if this is a proper CWD.
    if not os.path.exists(cwd(".cwd")):
        sys.exit(
            "No proper Findex Working Directory was identified, did you pass "
            "along the correct directory?"
        )

    check_configs()
    check_version()

    # # Determine if any CWD updates are required and if so, do them.
    current = open(cwd(".cwd"), "rb").read().strip()
    latest = open(cwd(".cwd", private=True), "rb").read().strip()
    if current != latest:
        migrate_cwd()
        open(cwd(".cwd"), "wb").write(latest)


def findex_main():
    """Findex main loop.
    """
    try:
        print("""Usage: findex [OPTION]...
  web           runs the web interface
        """)
    except KeyboardInterrupt:
        print("w00t")


@click.group(invoke_without_command=True)
@click.option("-d", "--debug", is_flag=True, help="Enable verbose logging")
@click.option("-q", "--quiet", is_flag=True, help="Only log warnings and critical messages")
@click.option("--nolog", is_flag=True, help="Don't log to file.")
@click.option("-m", "--maxcount", default=0, help="Maximum number of analyses to process")
@click.option("--user", help="Drop privileges to this user")
@click.option("--cwd", help="Findex Working Directory")
@click.pass_context
def main(ctx, debug, quiet, nolog, maxcount, user, cwd):
    """Invokes the Findex daemon or one of its subcommands.
    To be able to use different Findex configurations on the same machine with
    the same Findex installation, we use the so-called Findex Working
    Directory (aka "CWD"). A default CWD is available, but may be overridden
    through the following options - listed in order of precedence.
    \b
    * Command-line option (--cwd)
    * Environment option ("Findex_CWD")
    * Environment option ("Findex")
    * Current directory (if the ".cwd" file exists)
    * Default value ("~/.Findex")
    """
    decide_cwd(cwd)

    if quiet:
        level = logging.WARN
    elif debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    ctx.level = level

    # A subcommand will be invoked, so don't run Findex itself.
    if ctx.invoked_subcommand:
        return

    try:
        findex_init(level, ctx)
        findex_main()
    except FindexException as e:
        message = red("{0}: {1}".format(e.__class__.__name__, e))
        if len(log.handlers):
            log.critical(message)
        else:
            sys.stderr.write("{0}\n".format(message))
        sys.exit(1)
    except SystemExit as e:
        if e.code:
            print(e)
    except:
        # Deal with an unhandled exception.
        message = " ".join(platform.linux_distribution())
        print(message, traceback.format_exc())


@main.command()
@click.argument("args", nargs=-1)
@click.option("-H", "--host", default="localhost", help="Host to bind the Web Interface server on")
@click.option("-p", "--port", default=1337, help="Port to bind the Web Interface server on")
@click.option("--uwsgi", is_flag=True, help="Dump uWSGI configuration")
@click.option("--nginx", is_flag=True, help="Dump nginx configuration")
@click.pass_context
def web(ctx, args, host, port, uwsgi, nginx):
    """
    Operate the Findex Web Interface.
    @TODO: figure out uwsgi help thingy
    """
    logo(version)

    if nginx:
        # @TODO: nginx help msg here
        pass

    # Switch to findex/web and add the current path to sys.path as the Web
    # Interface is using local imports here and there.
    # TODO Rename local imports to either Findex.web.* or relative imports.
    os.chdir(findex_gui.__path__[0])  # os.chdir(os.path.join(findex_gui.__path__[0], "web"))
    sys.path.insert(0, ".")
    os.environ["FINDEX_APP"] = "web"
    os.environ["FINDEX_CWD"] = cwd()

    try:
        app_debug = config("findex:findex:debug")
        bind_host = host
        bind_port = port

        def run_sync():
            from findex_gui.web import app
            app.run(debug=app_debug, host=bind_host, port=bind_port, use_reloader=False)

        def run_async():
            from gevent import monkey
            monkey.patch_all()

            from gevent.pywsgi import WSGIServer
            from findex_gui.web import app

            http_server = WSGIServer((bind_host, bind_port), app)
            print(green(" * Running on http://%s:%s/ (Press CTRL+C to quit)") % (bind_host, str(bind_port)))
            http_server.serve_forever()

        if config("findex:findex:async"):
            run_async()
        else:
            run_sync()

    except Exception as e:
        message = red("{0}: {1}".format(e.__class__.__name__, e))
        if len(log.handlers):
            log.critical(message)
        else:
            sys.stderr.write("{0}\n".format(traceback.format_exc()))
        sys.exit(1)


def write_findex_conf(cfg=None):
    if cfg is None:
        cfg = {}

    # Merge any provided configuration with the defaults and emit their values.
    raw = {}
    for filename, sections in Config.configuration.items():
        cfg[filename] = cfg.get(filename, {})
        raw[filename] = {}
        for section, entries in sections.items():
            if section == "__star__":
                continue

            # Process each entry.
            if not isinstance(entries, (tuple, list)):
                entries = entries,

            for entry in entries:
                real_section = entry.get("__section__", section)
                entries = cfg[filename].get(section, {})
                entries.update(cfg[filename].get(real_section, {}))
                cfg[filename][real_section] = entries
                raw[filename][real_section] = {}
                for key, value in entry.items():
                    if key == "__section__":
                        continue

                    raw_value = cfg[filename][real_section].get(key, value.default)
                    cfg[filename][real_section][key] = raw_value
                    raw[filename][real_section][key] = value.emit(raw_value)

        if "__star__" in sections:
            section, key = sections["__star__"]
            for entry in cfg[filename][section][key]:
                if entry not in cfg[filename]:
                    raise ConfigError(
                        "A section was defined that has not been found: "
                        "%s:%s" % (section, entry)
                    )

                if isinstance(sections["*"], (tuple, list)):
                    section_types = sections["*"][0]
                else:
                    section_types = sections["*"]

                raw[filename][entry] = {}
                for key, value in section_types.items():
                    if key == "__section__":
                        continue

                    if key not in cfg[filename][entry]:
                        raw_value = cfg[filename][entry][key] = None
                    else:
                        raw_value = cfg[filename][entry][key]

                    raw[filename][entry][key] = value.emit(raw_value)

    def _config(s):
        filename, section, key = s.split(":")
        return cfg[filename][section][key]

    raw["config"] = _config
    for filename in os.listdir(cwd("cwd", "conf", private=True)):
        template = jinja2.Template(
            open(cwd("cwd", "conf", filename, private=True), "r").read()
        )
        open(cwd("conf", filename), "w").write(
            template.render(raw).rstrip() + "\n"
        )


