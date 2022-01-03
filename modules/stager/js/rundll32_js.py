import core.stager
import core.loader

class RunDLL32JSStager(core.stager.StagerWizard):

    NAME = "JScript rundll32.exe JavaScript Stager"
    DESCRIPTION = "Listens for new sessions, using JavaScript for payloads"
    AUTHORS = ['zerosum0x0']

    WORKLOAD = "js"

    def load(self):
        #self.options.set("SRVPORT", 9997)
        self.port = 9997

        self.stdlib = core.loader.load_script('data/stager/js/stdlib.js')
        self.stage = core.loader.load_script('data/stager/js/stage.js')
        self.stagetemplate = b"~SCRIPT~"
        self.stagecmd = core.loader.load_script("data/stager/js/rundll32_js/rundll32_js.cmd")
        self.forktemplate = core.loader.load_script("data/stager/js/mshta/template.hta")
        self.forkcmd = core.loader.load_script("data/stager/js/rundll32/rundll32.cmd")
        self.workload = "js"
