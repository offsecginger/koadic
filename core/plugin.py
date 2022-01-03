from core.linter import Linter
from core.options import Options
import core.loader
import copy
import string
import random

class Plugin(object):

    NAME = ""
    DESCRIPTION = ""
    AUTHORS = []

    def __init__(self, shell):
        self.options = Options()
        self.shell = shell

        self.job = self.job()

        self.load()

    ''' called when the framework starts '''
    def load(self):
        pass

    ''' called when the plugin is invoked '''
    def run(self):
        pass

    ''' job type of the associated plugin '''
    def job(self):
        pass

    def dispatch(self, workloads, job, checkrepeat=True, repeatzombie=''):
        if not repeatzombie:
            target = self.options.get("ZOMBIE")
        else:
            target = repeatzombie
        commas = [x.strip() for x in target.split(",")]

        splitted = []
        for x in commas:
            s = x.split("-")
            if len(s) == 1:
                splitted.append(str(x))
            else:
                for i in range(int(s[0]), int(s[1]) + 1):
                    splitted.append(str(i))

        self.ret_jobs = []
        for skey, session in self.shell.sessions.items():
            if (target.lower().strip() == "all" or str(session.id) in splitted) and not session.killed:
                if session.stager.WORKLOAD in workloads and session.fullystaged:
                    self.shell.print_verbose("Stager: %s Session %s" % (session.stager,session))
                    workload = workloads[session.stager.WORKLOAD]
                    options = copy.deepcopy(self.options)
                    j = job(self.shell, session.id, self.STATE, workload, options)
                    if j.create:
                        self.shell.jobs[j.key] = j
                        self.ret_jobs.append(j)
                        self.shell.update_restore = True

        if checkrepeat:
            if self.options.get("REPEAT") == "true":
                self.repeat(self.shell, workloads, self.options)

    def load_payload(self, id):
        try:
            for port in self.shell.stagers:
                for endpoint in self.shell.stagers[port]:
                    stager = self.shell.stagers[port][endpoint]
                    if int(stager.get_payload_id()) == int(id):
                        return stager.get_payload_data().decode()
        except:
            pass

        return None

    def parse_ips(self, ips):
        import core.cidr
        return core.cidr.get_ips(ips)

    def parse_ports(self, ports):
        import core.cidr
        return core.cidr.get_ports(ports)

    def make_vb_array(self, name, array):
        ret = "dim %s(%d)\n" % (name, len(array) - 1)

        count = 0
        for el in array:
            x = '%s(%d) = "%s"\n' % (name, count, str(el))
            ret += x
            count += 1

        return ret

    def make_js_array(self, name, array):
        array = ['"%s"' % item for item in array]
        ret = "var %s = [%s];" % (name, ", ".join(array))
        return ret

    def random_string(self, length):
        return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for n in range(length))

    def validate_shellcode(self, shellcode):
        if len(shellcode) % 2 != 0:
            return False

        return all(c in string.hexdigits for c in shellcode)

    def convert_shellcode(self, shellcode):
        decis = []
        count = 0
        for i in range(0, len(shellcode), 2):
            count += 1
            hexa = shellcode[i:i+2]
            deci = int(hexa, 16)

            if count % 25 == 0:
                decis.append(" _\\n" + str(deci))
            else:
                decis.append(str(deci))

        return ",".join(decis)
