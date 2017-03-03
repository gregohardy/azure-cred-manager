
import subprocess


class OSAgent(object):
    def shell(self, cmd):
        try:
            return subprocess.check_output(cmd.split(), universal_newlines=True)
        except Exception as e:
            raise Exception("Failed to execute the shell command [{0}] as [{1}]".format(cmd, str(e)))


