import collections
import tabulate
import traceback

class CredParse(object):

    def __init__(self, job):
        self.job = job
        self.shell = job.shell
        self.shell.update_restore = True
        self.j_ip = job.ip
        self.j_computer = "."
        if job.session_id != -1:
            self.session = job.session
            self.j_ip = self.session.ip
            self.j_computer = self.session.computer

    def new_cred(self):
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
        return cred

    def parse_hashdump_sam(self, data):

        # these are the strings to match on for secretsdump output
        s_sec_start = "[*] Dumping local SAM hashes (uid:rid:lmhash:nthash)\n"
        s_sec_end = "[*] Dumping cached domain logon information (uid:encryptedHash:longDomain:domain)"
        c_sec_start = "[*] Dumping cached domain logon information (uid:encryptedHash:longDomain:domain)\n"
        c_sec_end = "[*] Dumping LSA Secrets"

        output = data

        sam_sec = ""
        if s_sec_start in output:
            sam_sec1 = output.split(s_sec_start)[1]
            sam_sec2 = sam_sec1.split(s_sec_end)[0]
            sam_sec = sam_sec2.splitlines()

        cached_sec = ""
        if c_sec_start in output:
            cached_sec1 = output.split(c_sec_start)[1]
            cached_sec2 = cached_sec1.split(c_sec_end)[0]
            cached_sec = cached_sec2.splitlines()

        for htype in ["sam", "cached"]:
            hsec = locals().get(htype+"_sec")
            if not hsec or hsec[0].split()[0] == "[-]":
                continue
            for h in hsec:
                c = self.new_cred()
                c["IP"] = self.j_ip
                hparts = h.split(":")
                if len(hparts) < 4 or hparts[0][0] == '[':
                    continue
                c["Username"] = hparts[0]
                if htype == "sam":
                    c["NTLM"] = hparts[3]
                    c["Domain"] = self.j_computer
                else:
                    c["DCC"] = "$DCC2$10240#" + c["Username"] + "#" + hparts[1]
                    c["Domain"] = hparts[3]

                key = tuple([c["Domain"].lower(), c["Username"].lower()])

                domains = [j for i in self.shell.domain_info for j in i]
                if c["Domain"].lower() in domains:
                    domain_key = [i for i in self.shell.domain_info if c["Domain"].lower() in i][0]
                    other_domain = [i for i in domain_key if i != c["Domain"].lower()][0]
                else:
                    other_domain = ""

                other_key = tuple([other_domain, c["Username"].lower()])

                my_key = ""
                for creds_key in self.shell.creds_keys:
                    if creds_key == key or creds_key == other_key:
                        my_key = creds_key
                        break

                if my_key:
                    if c["IP"] != self.shell.creds[my_key]["IP"] and c["IP"] not in self.shell.creds[my_key]["Extra"]["IP"]:
                        self.shell.creds[my_key]["Extra"]["IP"].append(c["IP"])

                    if not self.shell.creds[my_key]["NTLM"] and c["NTLM"]:
                        self.shell.creds[my_key]["NTLM"] = c["NTLM"]
                    elif self.shell.creds[my_key]["NTLM"] != c["NTLM"] and c["NTLM"]:
                        if c["NTLM"] not in self.shell.creds[my_key]["Extra"]["NTLM"]:
                            self.shell.creds[my_key]["Extra"]["NTLM"].append(c["NTLM"])

                    if not self.shell.creds[my_key]["DCC"] and c["DCC"]:
                        self.shell.creds[my_key]["DCC"] = c["DCC"]
                    elif self.shell.creds[my_key]["DCC"] != c["DCC"] and c["DCC"]:
                        if c["DCC"] not in self.shell.creds[my_key]["Extra"]["DCC"]:
                            self.shell.creds[my_key]["Extra"]["DCC"].append(c["DCC"])
                else:
                    self.shell.creds_keys.append(key)
                    self.shell.creds[key] = c

        return

    def parse_mimikatz(self, data):
        if self.shell.verbose:
            self.shell.print_verbose("cred_parser::parse_mimikatz -> \n"+data+"\n<-")

        data = data.split("mimikatz(powershell) # ")[1]
        if "token::elevate" in data and "Impersonated !" in data:
            self.job.print_good("token::elevate -> got SYSTEM!")
            return

        if "privilege::debug" in data and "OK" in data:
            self.job.print_good("privilege::debug -> got SeDebugPrivilege!")
            return

        if "ERROR kuhl_m_" in data:
            self.job.error("0", data.split("; ")[1].split(" (")[0], "Error", data)
            self.job.errstat = 1
            return

        try:
            if "Authentication Id :" in data and ("sekurlsa::logonpasswords" in data.lower()
                    or "sekurlsa::msv" in data.lower()
                    or "sekurlsa::tspkg" in data.lower()
                    or "sekurlsa::wdigest" in data.lower()
                    or "sekurlsa::kerberos" in data.lower()
                    or "sekurlsa::ssp" in data.lower()
                    or "sekurlsa::credman" in data.lower()):
                from tabulate import tabulate
                nice_data = data.split('\n\n')
                cred_headers = ["msv","tspkg","wdigest","kerberos","ssp","credman"]
                msv_all = []
                tspkg_all = []
                wdigest_all = []
                kerberos_all = []
                ssp_all = []
                credman_all = []
                for section in nice_data:
                    if 'Authentication Id' in section:
                        msv = collections.OrderedDict()
                        tspkg = collections.OrderedDict()
                        wdigest = collections.OrderedDict()
                        kerberos = collections.OrderedDict()
                        ssp = collections.OrderedDict()
                        credman = collections.OrderedDict()

                        for index, cred_header in enumerate(cred_headers):
                            cred_dict = locals().get(cred_header)
                            try:
                                cred_sec1 = section.split(cred_header+" :\t")[1]
                            except:
                                continue
                            if index < len(cred_headers)-1:
                                cred_sec = cred_sec1.split("\t"+cred_headers[index+1]+" :")[0].splitlines()
                            else:
                                cred_sec = cred_sec1.splitlines()

                            for line in cred_sec:
                                if '\t *' in line:
                                    cred_dict[line.split("* ")[1].split(":")[0].rstrip()] = line.split(": ")[1].split("\n")[0]
                            if cred_dict:
                                cred_list = locals().get(cred_header+"_all")
                                cred_list.append(cred_dict)

                for cred_header in cred_headers:
                    cred_list = locals().get(cred_header+"_all")
                    tmp = [collections.OrderedDict(t) for t in set([tuple(d.items()) for d in cred_list])]
                    del cred_list[:]
                    cred_list.extend(tmp)

                parsed_data = "Results\n\n"

                for cred_header in cred_headers:
                    banner = cred_header+" credentials\n"+(len(cred_header)+12)*"="+"\n\n"
                    cred_dict = locals().get(cred_header+"_all")
                    if not cred_dict:
                        continue
                    cred_dict = sorted(cred_dict, key=lambda k: k['Username'])
                    ckeys = []
                    [[ckeys.append(k) for k in row if k not in ckeys] for row in cred_dict]
                    for cred in cred_dict:
                        key_d = cred["Domain"]
                        key_u = cred["Username"]
                        if "\\" in cred["Domain"]:
                            key_d = cred["Domain"].split("\\")[0]
                            key_u = cred["Domain"].split("\\")[1]
                        elif "\\" in cred["Username"]:
                            key_d = cred["Username"].split("\\")[0]
                            key_u = cred["Username"].split("\\")[1]

                        if "@" in cred["Domain"]:
                            key_d = cred["Domain"].split("@")[1]
                            key_u = cred["Domain"].split("@")[0]
                        elif "@" in cred["Username"]:
                            key_d = cred["Username"].split("@")[1]
                            key_u = cred["Username"].split("@")[0]

                        if cred["Domain"] == ".":
                            key_d = self.j_computer

                        key = tuple([key_d.lower(), key_u.lower()])

                        domains = [j for i in self.shell.domain_info for j in i]
                        if key_d.lower() in domains:
                            domain_key = [i for i in self.shell.domain_info if key_d.lower() in i][0]
                            other_domain = [i for i in domain_key if i != key_d.lower()][0]
                        else:
                            other_domain = ""

                        other_key = tuple([other_domain, key_u.lower()])

                        my_key = ""
                        for creds_key in self.shell.creds_keys:
                            if creds_key == key or creds_key == other_key:
                                my_key = creds_key

                        if not my_key:
                            self.shell.creds_keys.append(key)
                            c = self.new_cred()
                            c["IP"] = self.j_ip
                            for subkey in cred:
                                c[subkey] = cred[subkey]

                            if "\\" in c["Domain"]:
                                c["Username"] = c["Domain"].split("\\")[1]
                                c["Domain"] = c["Domain"].split("\\")[0]
                            elif "\\" in c["Username"]:
                                c["Domain"] = c["Username"].split("\\")[0]
                                c["Username"] = c["Username"].split("\\")[1]

                            if "@" in c["Domain"]:
                                c["Username"] = c["Domain"].split("@")[0]
                                c["Domain"] = c["Domain"].split("@")[1]
                            elif "@" in c["Username"]:
                                c["Domain"] = c["Username"].split("@")[1]
                                c["Username"] = c["Username"].split("@")[0]

                            if c["Domain"] == ".":
                                c["Domain"] = self.j_computer

                            if c["Password"] == "(null)":
                                c["Password"] = ""
                            if c["NTLM"].lower() == "d5024392098eb98bcc70051c47c6fbb2":
                                c["Password"] = "(null)"
                            if c["Password"][0:7] == "_TBAL_{" and c["Password"][-1] == "}":
                                c["Password"] = ""
                            self.shell.creds[key] = c

                        else:
                            key = my_key
                            if self.j_ip != self.shell.creds[key]["IP"] and self.j_ip not in self.shell.creds[key]["Extra"]["IP"]:
                                self.shell.creds[key]["Extra"]["IP"].append(self.j_ip)

                            if "Password" in cred:
                                cpass = cred["Password"]
                                if cpass[0:7] == "_TBAL_{" and cpass[-1] == "}":
                                    cpass = ""
                                if not self.shell.creds[key]["Password"] and cpass != "(null)" and cpass:
                                    self.shell.creds[key]["Password"] = cpass
                                elif self.shell.creds[key]["Password"] != cpass and cpass != "(null)" and cpass:
                                    if cpass not in self.shell.creds[key]["Extra"]["Password"]:
                                        self.shell.creds[key]["Extra"]["Password"].append(cpass)

                            if "NTLM" in cred:
                                cntlm = cred["NTLM"]
                                if not self.shell.creds[key]["NTLM"]:
                                    self.shell.creds[key]["NTLM"] = cntlm
                                    if cntlm.lower() == "d5024392098eb98bcc70051c47c6fbb2":
                                        self.shell.creds[key]["Password"] = "(null)"
                                elif self.shell.creds[key]["NTLM"] != cntlm and cntlm:
                                    if cntlm not in self.shell.creds[key]["Extra"]["NTLM"]:
                                        self.shell.creds[key]["Extra"]["NTLM"].append(cntlm)

                            if "SHA1" in cred:
                                csha1 = cred["SHA1"]
                                if not self.shell.creds[key]["SHA1"]:
                                    self.shell.creds[key]["SHA1"] = csha1
                                elif self.shell.creds[key]["SHA1"] != csha1 and csha1:
                                    if csha1 not in self.shell.creds[key]["Extra"]["SHA1"]:
                                        self.shell.creds[key]["Extra"]["SHA1"].append(csha1)

                            if "DPAPI" in cred:
                                cdpapi = cred["DPAPI"]
                                if not self.shell.creds[key]["DPAPI"]:
                                    self.shell.creds[key]["DPAPI"] = cdpapi
                                elif self.shell.creds[key]["DPAPI"] != cdpapi and cdpapi:
                                    if cdpapi not in self.shell.creds[key]["Extra"]["DPAPI"]:
                                        self.shell.creds[key]["Extra"]["DPAPI"].append(cdpapi)

                    separators = collections.OrderedDict([(k, "-"*len(k)) for k in ckeys])
                    cred_dict = [separators] + cred_dict
                    parsed_data += banner
                    parsed_data += tabulate(cred_dict, headers="keys", tablefmt="plain")
                    parsed_data += "\n\n"

                data = parsed_data

            if "SAMKey :" in data and "lsadump::sam" in data.lower():
                domain = data.split("Domain : ")[1].split("\n")[0]
                parsed_data = data.split("\n\n")
                for section in parsed_data:
                    if "RID  :" in section:
                        c = self.new_cred()
                        c["IP"] = self.j_ip
                        c["Username"] = section.split("User : ")[1].split("\n")[0]
                        c["Domain"] = domain
                        lm = ""
                        ntlm = ""
                        if "Hash LM: " in section:
                            lm = section.split("Hash LM: ")[1].split("\n")[0]
                        if "Hash NTLM: " in section:
                            ntlm = section.split("Hash NTLM: ")[1].split("\n")[0]
                        key = tuple([c["Domain"].lower(), c["Username"].lower()])

                        domains = [j for i in self.shell.domain_info for j in i]
                        if c["Domain"].lower() in domains:
                            domain_key = [i for i in self.shell.domain_info if c["Domain"].lower() in i][0]
                            other_domain = [i for i in domain_key if i != c["Domain"].lower()][0]
                        else:
                            other_domain = ""

                        other_key = tuple([other_domain, c["Username"].lower()])

                        my_key = ""
                        for creds_key in self.shell.creds_keys:
                            if creds_key == key or creds_key == other_key:
                                my_key = creds_key

                        if not my_key:
                            self.shell.creds_keys.append(key)
                            c["NTLM"] = ntlm
                            c["LM"] = lm
                            self.shell.creds[key] = c
                        else:
                            key = my_key
                            if c["IP"] != self.shell.creds[key]["IP"] and c["IP"] not in self.shell.creds[key]["Extra"]["IP"]:
                                self.shell.creds[key]["Extra"]["IP"].append(c["IP"])

                            if not self.shell.creds[key]["NTLM"] and ntlm:
                                self.shell.creds[key]["NTLM"] = ntlm
                            elif self.shell.creds[key]["NTLM"] != ntlm and ntlm:
                                if ntlm not in self.shell.creds[key]["Extra"]["NTLM"]:
                                    self.shell.creds[key]["Extra"]["NTLM"].append(ntlm)

                            if not self.shell.creds[key]["LM"] and lm:
                                self.shell.creds[key]["LM"] = lm
                            elif self.shell.creds[key]["LM"] != lm and lm:
                                if lm not in self.shell.creds[key]["Extra"]["LM"]:
                                    self.shell.creds[key]["Extra"]["LM"].append(lm)

            return data
        except Exception as e:
            data += "\n\n\n"
            data += traceback.format_exc()
            return data

    def parse_pypykatz(self, json_results):
        try:
            from tabulate import tabulate
            logon_sessions = json_results['logon_sessions']
            cred_headers = ["msv","tspkg","wdigest","kerberos","ssp","credman"]
            msv_all = []
            tspkg_all = []
            wdigest_all = []
            kerberos_all = []
            ssp_all = []
            credman_all = []

            translation = {
                'username': 'Username',
                'domainname': 'Domain',
                'NThash': 'NTLM',
                'SHAHash': 'SHA1',
                'LMHash': 'LM',
                'password': 'Password'
            }

            for l in logon_sessions:
                current_session = logon_sessions[l]
                msv = collections.OrderedDict()
                tspkg = collections.OrderedDict()
                wdigest = collections.OrderedDict()
                kerberos = collections.OrderedDict()
                ssp = collections.OrderedDict()
                credman = collections.OrderedDict()

                for index, cred_header in enumerate(cred_headers):
                    cred_dict = locals().get(cred_header)
                    cred_sec = current_session[cred_header+'_creds']
                    if cred_sec:
                        for i in cred_sec:
                            for k in i:
                                if type(i[k]) == list or k == 'luid' or k == 'credtype':
                                    continue
                                if k in translation and i[k]:
                                    cred_dict[translation[k]] = i[k]
                    if cred_dict:
                        cred_list = locals().get(cred_header+"_all")
                        cred_list.append(cred_dict)

            for cred_header in cred_headers:
                cred_list = locals().get(cred_header+"_all")
                tmp = [collections.OrderedDict(t) for t in set([tuple(d.items()) for d in cred_list])]
                del cred_list[:]
                cred_list.extend(tmp)

            parsed_data = "Results\n\n"

            for cred_header in cred_headers:
                banner = cred_header+" credentials\n"+(len(cred_header)+12)*"="+"\n\n"
                cred_dict = locals().get(cred_header+"_all")
                if not cred_dict:
                    continue
                # if cred_header == 'tspkg':
                #     try:
                #         cred_dict = sorted(cred_dict, key=lambda k: k['Domain'])
                #     except:
                #         continue
                else:
                    try:
                        cred_dict = sorted(cred_dict, key=lambda k: k['Username'])
                    except:
                        continue
                ckeys = []
                [[ckeys.append(k) for k in row if k not in ckeys] for row in cred_dict]
                for cred in cred_dict:
                    if "Domain" not in cred:
                        cred["Domain"] = "."
                        ckeys.append("Domain")
                    # if cred_header == 'tspkg':
                    #     tmp = cred["Domain"]
                    #     cred["Domain"] = cred["Username"]
                    #     cred["Username"] = tmp
                    key_d = cred["Domain"]
                    key_u = cred["Username"]
                    if "\\" in cred["Domain"]:
                        key_d = cred["Domain"].split("\\")[0]
                        key_u = cred["Domain"].split("\\")[1]
                    elif "\\" in cred["Username"]:
                        key_d = cred["Username"].split("\\")[0]
                        key_u = cred["Username"].split("\\")[1]

                    if "@" in cred["Domain"]:
                        key_d = cred["Domain"].split("@")[1]
                        key_u = cred["Domain"].split("@")[0]
                    elif "@" in cred["Username"]:
                        key_d = cred["Username"].split("@")[1]
                        key_u = cred["Username"].split("@")[0]

                    if cred["Domain"] == ".":
                        key_d = self.j_computer

                    key = tuple([key_d.lower(), key_u.lower()])

                    domains = [j for i in self.shell.domain_info for j in i]
                    if key_d.lower() in domains:
                        domain_key = [i for i in self.shell.domain_info if key_d.lower() in i][0]
                        other_domain = [i for i in domain_key if i != key_d.lower()][0]
                    else:
                        other_domain = ""

                    other_key = tuple([other_domain, key_u.lower()])

                    my_key = ""
                    for creds_key in self.shell.creds_keys:
                        if creds_key == key or creds_key == other_key:
                            my_key = creds_key

                    if not my_key:
                        self.shell.creds_keys.append(key)
                        c = self.new_cred()
                        c["IP"] = self.j_ip
                        # translation = {
                        #     'username': 'Username',
                        #     'domainname': 'Domain',
                        #     'NThash': 'NTLM',
                        #     'LMHash': 'LM',
                        #     'SHAHash': 'SHA1',
                        #     'password': 'Password',
                        # }
                        for subkey in cred:
                            # if subkey in translation:
                            c[subkey] = cred[subkey]

                        if "\\" in c["Domain"]:
                            c["Username"] = c["Domain"].split("\\")[1]
                            c["Domain"] = c["Domain"].split("\\")[0]
                        elif "\\" in c["Username"]:
                            c["Domain"] = c["Username"].split("\\")[0]
                            c["Username"] = c["Username"].split("\\")[1]

                        if "@" in c["Domain"]:
                            c["Username"] = c["Domain"].split("@")[0]
                            c["Domain"] = c["Domain"].split("@")[1]
                        elif "@" in c["Username"]:
                            c["Domain"] = c["Username"].split("@")[1]
                            c["Username"] = c["Username"].split("@")[0]

                        if c["Domain"] == ".":
                            c["Domain"] = self.j_computer

                        if c["Password"] == "(null)":
                            c["Password"] = ""
                        if c["NTLM"].lower() == "d5024392098eb98bcc70051c47c6fbb2":
                            c["Password"] = "(null)"
                        if c["Password"][0:7] == "_TBAL_{" and c["Password"][-1] == "}":
                            c["Password"] = ""
                        self.shell.creds[key] = c

                    else:
                        key = my_key
                        if self.j_ip != self.shell.creds[key]["IP"] and self.j_ip not in self.shell.creds[key]["Extra"]["IP"]:
                            self.shell.creds[key]["Extra"]["IP"].append(self.j_ip)

                        if "Password" in cred:
                            cpass = cred["Password"]
                            if cpass[0:7] == "_TBAL_{" and cpass[-1] == "}":
                                cpass = ""
                            if not self.shell.creds[key]["Password"] and cpass != "(null)" and cpass:
                                self.shell.creds[key]["Password"] = cpass
                            elif self.shell.creds[key]["Password"] != cpass and cpass != "(null)" and cpass:
                                if cpass not in self.shell.creds[key]["Extra"]["Password"]:
                                    self.shell.creds[key]["Extra"]["Password"].append(cpass)

                        if "NTLM" in cred:
                            cntlm = cred["NTLM"]
                            if not self.shell.creds[key]["NTLM"]:
                                self.shell.creds[key]["NTLM"] = cntlm
                                if cntlm.lower() == "d5024392098eb98bcc70051c47c6fbb2":
                                    self.shell.creds[key]["Password"] = "(null)"
                            elif self.shell.creds[key]["NTLM"] != cntlm and cntlm:
                                if cntlm not in self.shell.creds[key]["Extra"]["NTLM"]:
                                    self.shell.creds[key]["Extra"]["NTLM"].append(cntlm)

                        if "SHA1" in cred:
                            csha1 = cred["SHA1"]
                            if not self.shell.creds[key]["SHA1"]:
                                self.shell.creds[key]["SHA1"] = csha1
                            elif self.shell.creds[key]["SHA1"] != csha1 and csha1:
                                if csha1 not in self.shell.creds[key]["Extra"]["SHA1"]:
                                    self.shell.creds[key]["Extra"]["SHA1"].append(csha1)

                        if "DPAPI" in cred:
                            cdpapi = cred["DPAPI"]
                            if not self.shell.creds[key]["DPAPI"]:
                                self.shell.creds[key]["DPAPI"] = cdpapi
                            elif self.shell.creds[key]["DPAPI"] != cdpapi and cdpapi:
                                if cdpapi not in self.shell.creds[key]["Extra"]["DPAPI"]:
                                    self.shell.creds[key]["Extra"]["DPAPI"].append(cdpapi)

                separators = collections.OrderedDict([(k, "-"*len(k)) for k in ckeys])
                cred_dict = [separators] + cred_dict
                parsed_data += banner
                parsed_data += tabulate(cred_dict, headers="keys", tablefmt="plain")
                parsed_data += "\n\n"

            data = parsed_data

            return data
        except Exception as e:
            data += "\n\n\n"
            data += traceback.format_exc()
            return data
