#!/usr/bin/env python
import os
import setuptools
import traceback


def githash():
    """Extracts the current Git hash."""
    # Code borrowed from 'Cuckoo Sandbox' (https://github.com/cuckoosandbox/cuckoo)
    # Credits go to @jbremer (Jurriaan Bremer) and the Cuckoo team
    git_head = os.path.join(".git", "HEAD")
    if os.path.exists(git_head):
        head = open(git_head, "r").read().strip()
        if not head.startswith("ref: "):
            return head

        git_ref = os.path.join(".git", head.split()[1])
        if os.path.exists(git_ref):
            return open(git_ref, "r").read().strip()

cwd_public = os.path.join("findex_gui", "data")
cwd_private = os.path.join("findex_gui", "data-private")
open(os.path.join(cwd_private, ".cwd"), "w").write(githash() or "")


def do_setup(**kwargs):
    try:
        setuptools.setup(**kwargs)
    except (SystemExit, Exception) as e:
        print("\x1b[31m")
        print("The following error has occurred while trying to install Findex!")
        print("\x1b[0m")
        print(traceback.format_exc(),)
        print("\x1b[31m")
        print("Make sure that you've installed all requirements for Findex ")
        print("to be installed properly!")
        print("\x1b[33m")
        print("Once you have triple checked that all dependencies have been ")
        print("installed but Findex still fails, please feel free to reach ")
        print("out to us on Github!")
        print("\x1b[0m")

        if isinstance(e, ValueError) and "jpeg is required" in e.message:
            print("  This particular error may be resolved as follows:")
            print("      sudo apt-get install libjpeg-dev")

        if isinstance(e, ValueError) and "zlib is required" in e.message:
            print("  This particular error may be resolved as follows:")
            print("      sudo apt-get install zlib1g-dev")

        if isinstance(e, SystemExit) and "x86_64-linux-gnu-gcc" in e.message:
            print("  This particular error *may* be resolved as follows:")
            print("      sudo apt-get install python-dev libffi-dev libssl-dev")

do_setup(
    name="Findex-GUI",
    version="0.2.18",
    author="Sander Ferdinand",
    author_email="sa.ferdinand@gmail.com",
    packages=[
        "findex_gui",
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Environment :: Console",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Framework :: Pytest",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.5",
        "Topic :: Security",
    ],
    keywords=(
        "findex ftp http smb crawler search engine"
    ),
    url="https://github.com/skftn/findex-gui",
    license="MIT",
    description="Multi-purpose search engine for various protocols.",
    long_description=open("README.md", "r").read(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "findex = findex_gui.main:main",
        ],
    },
    install_requires=[
        "gevent==1.2.1",
        "flask==0.12.2",
        "click",
        "findex_common",
        "flask-wtf==0.14.2",
        "flask-auth==0.85",
        "flask-yoloapi==0.0.6",
        "psycopg2==2.7.1",
        "sqlalchemy>=1.1.6",
        "sqlalchemy-utils>=0.32.13",
        "sqlalchemy-zdb>=0.1.0",
        "jinja2",
        "furl==0.5.7",
        "flask-babel",
        "humanfriendly==3.2",
        "IPy==0.83",
        "pysocks",
        "python-magic",
        "requests[security]",
        "markupsafe",
        "sqlalchemy-json",
        "pika",
        "dsnparse==0.1.10"
    ],
    setup_requires=[
        "pytest-runner",
    ],
    tests_require=[
        "coveralls",
        "pytest",
        "pytest-cov",
        "pytest-django",
        "pytest-pythonpath",
        "mock==2.0.0",
        "responses==0.5.1"
    ],
)
