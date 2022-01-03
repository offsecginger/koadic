import core.implant

class EnumPrintersJob(core.job.Job):
    def done(self):
        self.display()

    def display(self):
        self.shell.print_plain("Printer Connections:")
        self.shell.print_plain(self.data)
        self.results = self.data

class EnumPrintersImplant(core.implant.Implant):
    
    NAME = "Enumerate Printer Connections"
    DESCRIPTION = "Enumerates all Printer Connections"
    AUTHORS = ["Tony M Lambert @ForensicITGuy"]
    STATE = "implant/gather/enum_printers"

    def load(self):
        pass    
    
    def job(self):
        return EnumPrintersJob

    def run(self):
        payloads = {}
        payloads["js"] = "data/implant/gather/enum_printers.js"
        self.dispatch(payloads, self.job)

    
