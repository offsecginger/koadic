import core.stager
import core.loader

class BitsadminStager(core.stager.StagerWizard):

    NAME = "JScript Bitsadmin Stager"
    DESCRIPTION = "Listens for new sessions, using JScript Bitsadmin for payloads"
    AUTHORS = ['zerosum0x0']

    WORKLOAD = "js"

    def __init__(self, shell):
        super(BitsadminStager, self).__init__(shell) # stupid hack inc!
        self.options.set("ENDPOINTTYPE", ".wsf")
        self.options.set("OBFUSCATE", "")

    def load(self):
        #self.options.set("SRVPORT", 9999)
        self.port = 9995

        self.stdlib = core.loader.load_script('data/stager/js/stdlib.js')
        self.stage = core.loader.load_script('data/stager/js/stage.js')
        self.stagetemplate = core.loader.load_script("data/stager/js/bitsadmin/template.wsf")
        self.stagecmd = core.loader.load_script("data/stager/js/bitsadmin/bitsadmin.cmd")
        self.forktemplate = core.loader.load_script("data/stager/js/mshta/template.hta")
        self.forkcmd = core.loader.load_script("data/stager/js/rundll32/rundll32.cmd")
        self.workload = "js"
