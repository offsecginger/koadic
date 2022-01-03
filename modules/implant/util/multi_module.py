import core.implant
import time
import string

class MultiModuleImplant(core.implant.Implant):

    NAME = "Multi Module Execution"
    DESCRIPTION = "Run multiple modules in succession"
    AUTHORS = ["TheNaterz"]
    STATE = "implant/util/multi_module"

    def load(self):
        self.options.register("MODULES", "", "Modules to run in succession (comma seperated)", required = True)
        self.options.register("DELAY", "0", "Number of seconds between each job", required = True)

    def run(self):
        for module in self.options.get("MODULES").split(","):
            plugin = self.shell.plugins[module.strip()]
            old_zombie = plugin.options.get("ZOMBIE")
            plugin.options.set("ZOMBIE", self.options.get("ZOMBIE"))
            plugin.run()
            plugin.options.set("ZOMBIE", old_zombie)

            delay = int(self.options.get("DELAY"))
            if delay > 0:
                time.sleep(delay)

