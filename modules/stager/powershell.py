import os
import sys
import core.stager
import random

"""
class PowerShellStager(core.stager.Stager):

    NAME = "PowerShell Stager"
    DESCRIPTION = "Listens for new sessions, using PowerShell for payloads"
    AUTHORS = ['RiskSense, Inc.']

    def run(self):
        payloads = {}
        payloads["In Memory"] = self.load_file("data/stager/powershell/memory.cmd")

        self.start_server(payloads)

    def stage(self, server, handler, session):
        script = self.load_script("data/stager/powershell/payload.ps1")
        handler.send_ok(script)
"""
