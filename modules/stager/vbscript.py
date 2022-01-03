import os
import sys
import core.stager
from core.payload import Payload
import random

"""
class VBScriptStager(core.stager.Stager):

    NAME = "VBScript Stager"
    DESCRIPTION = "Listens for new sessions, using VBScript for payloads"
    AUTHORS = ['RiskSense, Inc.']

    # the type of job payloads
    WORKLOAD = "vbs"

    def run(self):
        payloads = []
        payloads.append(Payload("In Memory (Windows 2000 SP3+)", self.load_file("data/stager/vbscript/mshta.cmd")))
        payloads.append(Payload("On Disk (All Windows)", self.load_file("data/stager/vbscript/disk.cmd")))

        self.start_server(payloads)

    def stage(self, server, handler, session, options):
        script = self.load_script("data/stager/vbscript/work.vbs", options, True, False)
        handler.reply(200, script)

    def job(self, server, handler, session, job, options):
        script = self.load_script("data/stager/vbscript/job.vbs", options)
        handler.reply(200, script)
"""
