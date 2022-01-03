#!/usr/bin/python3

import collections
import tabulate
import traceback
import sys
import json

from pypykatz.pypykatz import pypykatz
from pypykatz.commons.common import UniversalEncoder

def parse_pypykatz(json_results):
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

            for cred_header in cred_headers:
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
                    for thing in ['Password', 'NTLM', 'LM', 'SHA1']:
                        if thing in cred_dict:
                            cred_list = locals().get(cred_header+"_all")
                            cred_list.append(cred_dict)
                            break

        for cred_header in cred_headers:
            cred_list = locals().get(cred_header+"_all")
            tmp = [collections.OrderedDict(t) for t in set([tuple(d.items()) for d in cred_list])]
            del cred_list[:]
            cred_list.extend(tmp)

        parsed_data = ""

        for cred_header in cred_headers:
            banner = cred_header+" credentials\n"+(len(cred_header)+12)*"="+"\n\n"
            cred_dict = locals().get(cred_header+"_all")
            if not cred_dict:
                continue
            if cred_header == 'tspkg':
                try:
                    cred_dict = sorted(cred_dict, key=lambda k: k['Domain'])
                except:
                    continue
            else:
                try:
                    cred_dict = sorted(cred_dict, key=lambda k: k['Username'])
                except:
                    continue
            ckeys = []
            [[ckeys.append(k) for k in row if k not in ckeys] for row in cred_dict]

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

if len(sys.argv)!= 2:
    print("Usage: ./parse_mimikatz LSASS.DMP")
    sys.exit()

mimi = pypykatz.parse_minidump_file(sys.argv[1])
json_results = json.loads(json.dumps([mimi], cls = UniversalEncoder))[0]

print(parse_pypykatz(json_results))
