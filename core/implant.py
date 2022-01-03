import core.plugin
import threading

class Implant(core.plugin.Plugin):
    RJOB_ID = 0
    RJOB_ID_LOCK = threading.Lock()

    def __init__(self, shell):
        super(Implant, self).__init__(shell)
        self.options.register("ZOMBIE", "ALL", "the zombie to target")
        self.options.register("IGNOREADMIN", "false", "ignore session elevation restrictions", enum=["true", "false"], advanced=True)
        self.options.register("IGNOREBUILD", "false", "ignore build number", enum=["true", "false"], advanced=True)
        self.options.register("REPEAT", "false", "Run the implant multiple times", boolean = True, advanced = True)
        self.options.register("REPEATTIME", "600", "Seconds between running implant", advanced = True)
        self.options.register("REPEATCYCLES", "3", "Number of times to run (0 = indefinite)", advanced = True)

    def repeat(self, shell, workloads, options):
        rt = int(self.options.get("REPEATTIME"))
        rc = int(self.options.get("REPEATCYCLES"))
        state = self.STATE
        with Implant.RJOB_ID_LOCK:
            key = str(Implant.RJOB_ID)
            Implant.RJOB_ID += 1
        shell.repeatjobs[key] = [rt, rc, workloads, self.job, rt, state, options, self]
