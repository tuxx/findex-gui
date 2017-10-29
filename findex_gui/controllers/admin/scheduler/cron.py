import os
import tempfile

from findex_gui.main import python_env


class CronController:
    @staticmethod
    def has_cronjob():
        crontab = os.popen("crontab -l").read()
        cronjob = CronController.generate_cronjob()
        if cronjob in crontab:
            return True
        return

    @staticmethod
    def insert_cronjob(job, default_time="*/1 * * * *"):
        """
        Insert a command into cronjobs
        :param job: the command
        :param default_time: every 1 min is default
        :return:
        """
        tmp_file = tempfile.mkstemp("_fincron")[1]
        crontab = os.popen("crontab -l").read()
        if "no crontab for" not in crontab.lower():
            crontab += "\n%s %s\n" % (default_time, job)

        f = open(tmp_file, "w")
        f.write(crontab)
        f.close()

        os.popen("crontab %s" % tmp_file).read()
        os.remove(tmp_file)

    @staticmethod
    def remove_cronjob():
        crontab = os.popen("crontab -l").read()
        cronjob = CronController.generate_cronjob()

        new_lines = []
        for line in crontab.split("\n"):
            if cronjob not in line and line != cronjob:
                new_lines.append(line)
        new_crontab = "\n".join(new_lines)

        if not new_crontab.endswith("\n"):
            new_crontab += "\n"

        tmp_file = tempfile.mkstemp("_fincron")[1]

        f = open(tmp_file, "w")
        f.write(new_crontab)
        f.close()

        os.popen("crontab %s" % tmp_file).read()
        os.remove(tmp_file)

    @staticmethod
    def generate_cronjob():
        return " ".join([
            "cd %s &&" % python_env["project_root"],
            python_env["interpreter"],
            "%s/findex" % os.path.dirname(python_env["interpreter"]),
            "scheduler"
        ])
