import json
import subprocess
import os
import tempfile

import dsnparse
from findex_common.crawl.crawl import CrawlController
from findex_gui.main import python_env
from findex_gui.bin.config import config
from findex_gui.bin.utils import log_msg


class Crawler:
    @staticmethod
    def can_crawl():
        path_twistd = "%s/twistd" % os.path.dirname(python_env["interpreter"])
        path_fincrawl = "%s/findex-crawl/" % python_env["project_root"]
        path_fincrawl_rpc = "%srpc.py" % path_fincrawl

        if not os.path.isfile(path_twistd):
            raise Exception("twistd not found (%s)" % path_twistd)

        if not os.path.isfile(path_fincrawl_rpc):
            raise Exception("findex-crawl directory not found (%s)" % path_fincrawl_rpc)

        return True

    @staticmethod
    def spawn(tasks, queue_size=5):
        """
        Spawns the crawler in 'DIRECT' mode. The suggested way
        is to use AMQP instead.
        :param tasks:
        :param queue_size:
        :return:
        """
        path_fincrawl = "%s/findex-crawl/" % python_env["project_root"]
        log_msg("Spawning local crawler in DIRECT mode for %d tasks" % len(tasks))

        # construct tasks json file
        blobs = []
        for t in tasks:
            crawl_message = CrawlController.crawl_message_make(t)
            if not crawl_message:
                continue
            blobs.append(crawl_message)

        try:
            crawl_messages = json.dumps(blobs, indent=4, sort_keys=True)
            crawl_file = tempfile.mkstemp("_fincrawl.json")[1]
        except Exception as ex:
            log_msg(":%s" % (str(ex)), level=3)
            return

        print(crawl_messages)

        # write tmp tasks file for the crawler
        f = open(crawl_file, "w")
        f.write(crawl_messages)
        f.close()

        dsn = dsnparse.parse(config("findex:database:connection"))

        dsn_blob = {
            "user": dsn.username,
            "pass": dsn.password,
            "host": dsn.host,
            "port": 5432 if not isinstance(dsn.port, int) else dsn.port,
            "db": dsn.paths[0]
        }

        # set env variables
        shell_env = os.environ.copy()  # should include the current python virtualenv
        shell_env["FINDEX_CRAWL_MODE"] = "DIRECT"
        shell_env["FINDEX_CRAWL_FILE"] = crawl_file
        shell_env["FINDEX_CRAWL_FILE_CLEANUP"] = ":-D"
        shell_env["FINDEX_CRAWL_LOG_VERBOSITY"] = "20"
        shell_env["FINDEX_CRAWL_QUEUE_SIZE"] = str(queue_size)

        for k, v in dsn_blob.items():
            shell_env["FINDEX_CRAWL_DB_%s" % k.upper()] = str(v)

        for k, v in shell_env.items():
            if k.startswith("FINDEX_CRAWL"):
                print("export %s=\"%s\"" % (k, str(v)))

        # non-blocking Popen
        # for some reason `/bin/bash -c` is needed, else it cant find the relative `rpc.py`, even tough `cwd=` is set
        command = ["/bin/bash", "-c",
                   "%s/twistd -ony rpc.py &" % os.path.dirname(python_env["interpreter"])]

        print("spawning shell: %s" % " ".join(command))
        subprocess.Popen(command, cwd=path_fincrawl,
                         env=shell_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         universal_newlines=True, preexec_fn=os.setpgrp)
