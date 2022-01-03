DESCRIPTION = "shows collected credentials"

def autocomplete(shell, line, text, state):
    if "-d" in line.split():
        options = [x + " " for y in shell.domain_info for x in y if x.upper().startswith(text.upper())]
        try:
            return options[state]
        except:
            return None

def help(shell):
    shell.print_plain("")
    shell.print_plain("Use %s to sort on a column name" % (shell.colors.colorize("creds --sort column", shell.colors.BOLD)))
    shell.print_plain("Use %s to lazy search across credentials" % (shell.colors.colorize("creds --search text", shell.colors.BOLD)))
    shell.print_plain("Use %s for full credential details" % (shell.colors.colorize("creds -a", shell.colors.BOLD)))
    shell.print_plain("Use %s for specific user credentials (add --like for partial names)" % (shell.colors.colorize("creds -u user1,user2,user3,...", shell.colors.BOLD)))
    shell.print_plain("Use %s for domain admin credentials" % (shell.colors.colorize("creds -d domain", shell.colors.BOLD)))
    shell.print_plain("Use %s for domain credentials" % (shell.colors.colorize("creds -D domain", shell.colors.BOLD)))
    shell.print_plain("Use %s to write credentials to a file" % (shell.colors.colorize("creds -x", shell.colors.BOLD)))
    shell.print_plain("Use %s to edit credentials" % (shell.colors.colorize("creds --edit", shell.colors.BOLD)))
    shell.print_plain("")
    shell.print_plain("NOTE: A listing that ends in [+] means extra information is available.")
    shell.print_plain("")

def print_creds(shell, sortcol="Normal", domain="", search=""):

    domains = []
    if domain:
        domains = [j for i in shell.domain_info for j in i]
        if not domain.lower() in domains:
            shell.print_warning("\nDomain information not gathered, results may not be complete")

    formats = "\t{0:9}{1:17}{2:<20}{3:<20}{4:<25}{5:<42}"

    results = []

    for key in shell.creds_keys:
        if (shell.creds[key]["Username"][-1] == '$' or
            (not shell.creds[key]["Password"] and
                not shell.creds[key]["NTLM"]) or
            shell.creds[key]["NTLM"] == '31d6cfe0d16ae931b73c59d7e0c089c0'):

            continue
        else:
            result_cred = dict(shell.creds[key])
            result_cred["Cred ID"] = str(shell.creds_keys.index(key))
            results.append(result_cred)

    if sortcol != "Normal":
        colname = [c for c in list(results[0].keys()) if c.lower() == sortcol.lower()]
        if not colname:
            shell.print_error("Column '"+sortcol+"' does not exist!")
            return
        results = sorted(results, key=lambda k: k[colname[0]])

    shell.print_plain("")

    shell.print_plain(formats.format("Cred ID", "IP", "USERNAME", "DOMAIN", "PASSWORD", "NTLM"))
    shell.print_plain(formats.format("-"*7, "--", "-"*8,  "-"*6, "-"*8, "-"*4))

    for r in results:

        if search:
            searchflag = False

        if search and search.lower() in r["Cred ID"].lower():
            searchflag = True

        if search and search.lower() in r["IP"].lower():
            searchflag = True

        if search and search.lower() in r["NTLM"].lower():
            searchflag = True

        tmpuser = r["Username"]
        if search and search.lower() in tmpuser.lower():
            searchflag = True
        if len(tmpuser) > 18:
            tmpuser = tmpuser[:15] + "..."

        tmpdomain = r["Domain"]
        if search and search.lower() in tmpdomain.lower():
            searchflag = True
        if domains:
            if not tmpdomain.lower() in domains:
                continue
        elif domain and domain.lower() != tmpdomain.lower():
                continue
        if len(tmpdomain) > 18:
            tmpdomain = tmpdomain[:15] + "..."

        tmppass = r["Password"]
        if search and search.lower() in tmppass.lower():
            searchflag = True
        if len(tmppass) > 23:
            tmppass = tmppass[:20] + "..."
        extraflag = ""
        for key in ["Password", "SHA1", "DCC", "DPAPI", "LM"]:
            if r["Extra"][key]:
                extraflag = "[+]"
                break

        if search and not searchflag:
            continue

        shell.print_plain(formats.format(r["Cred ID"], r["IP"], tmpuser, tmpdomain, tmppass, r["NTLM"])+extraflag)

    shell.print_plain("")

def print_creds_detailed(shell, users="*", like_flag=False):
    shell.print_plain("")

    for key in shell.creds_keys:
        if (users == "*" or
            shell.creds[key]["Username"].lower() in [u.lower() for u in users.split(",")] or
            (str(shell.creds_keys.index(key)) in [u.lower() for u in users.split(",")] and
                not like_flag) or
            (len([u for u in users.split(",") if u.lower() in shell.creds[key]["Username"].lower()]) > 0 and
                like_flag)):

            shell.print_plain("Cred ID: "+str(shell.creds_keys.index(key)))
            shell.print_plain("IP: "+shell.creds[key]["IP"]+" "+" ".join(shell.creds[key]["Extra"]["IP"]))
            shell.print_plain("USERNAME: "+shell.creds[key]["Username"])
            shell.print_plain("DOMAIN: "+shell.creds[key]["Domain"])
            shell.print_plain("PASSWORD: "+shell.creds[key]["Password"]+" "+" ".join(shell.creds[key]["Extra"]["Password"]))
            shell.print_plain("NTLM: "+shell.creds[key]["NTLM"]+" "+" ".join(shell.creds[key]["Extra"]["NTLM"]))
            shell.print_plain("LM: "+shell.creds[key]["LM"]+" "+" ".join(shell.creds[key]["Extra"]["LM"]))
            shell.print_plain("SHA1: "+shell.creds[key]["SHA1"]+" "+" ".join(shell.creds[key]["Extra"]["SHA1"]))
            shell.print_plain("DCC: "+shell.creds[key]["DCC"]+" "+" ".join(shell.creds[key]["Extra"]["DCC"]))
            shell.print_plain("DPAPI: "+shell.creds[key]["DPAPI"]+" "+" ".join(shell.creds[key]["Extra"]["DPAPI"]))
            shell.print_plain("")

def print_creds_das(shell, domain):
    domains = [j for i in shell.domain_info for j in i]
    if not domain.lower() in domains:
        shell.print_error("Supplied domain not known")
        return

    domain_key = [i for i in shell.domain_info if domain.lower() in i][0]
    alt_domain = [i for i in domain_key if i != domain][0]

    if not "Domain Admins" in shell.domain_info[domain_key]:
        shell.print_error("Domain Admins not gathered for target domain. Please run implant/gather/enum_domain_info")
        return

    das = shell.domain_info[domain_key]["Domain Admins"]

    # formats = "\t{0:9}{1:17}{2:<20}{3:<20}{4:<25}{5:<10}"
    formats = "\t{0:9}{1:17}{2:<20}{3:<20}{4:<34}{5:<10}"
    shell.print_plain("")

    # shell.print_plain(formats.format("Cred ID", "IP", "USERNAME", "DOMAIN", "PASSWORD", "HASH"))
    # shell.print_plain(formats.format("-"*7, "--", "-"*8,  "-"*6, "-"*8, "-"*4))
    shell.print_plain(formats.format("Cred ID", "IP", "USERNAME", "DOMAIN", "PASS / HASH", "TYPE"))
    shell.print_plain(formats.format("-"*7, "--", "-"*8,  "-"*6, "-"*11, "-"*4))
    for key in shell.creds_keys:
        # credpass = shell.creds[key]["Password"]
        creduser = shell.creds[key]["Username"]
        creddomain = shell.creds[key]["Domain"]
        # credntlm = shell.creds[key]["NTLM"]
        if (creduser.lower() in das and
            (creddomain.lower() == domain.lower() or
                creddomain.lower() == alt_domain.lower())):
            #     creddomain.lower() == alt_domain.lower()) and
            # (credpass or
            #     credntlm)):

            # if len(credpass) > 23:
            #     credpass = credpass[:20] + "..."
            # if len(creduser) > 18:
            #         creduser = creduser[:15] + "..."
            # if len(creddomain) > 18:
            #     creddomain = creddomain[:15] + "..."
            # shell.print_plain(formats.format(str(shell.creds_keys.index(key)), shell.creds[key]["IP"], creduser, creddomain, credpass, shell.creds[key]["NTLM"]))

            for credtype in ["Password", "NTLM", "LM", "SHA1", "DCC", "DPAPI"]:
                if shell.creds[key][credtype]:
                    credcred = shell.creds[key][credtype]
                    if len(credcred) > 32:
                        credcred = credcred[:29] + "..."
                    if len(creduser) > 18:
                        creduser = creduser[:15] + "..."
                    if len(creddomain) > 18:
                        creddomain = creddomain[:15] + "..."

                    shell.print_plain(formats.format(str(shell.creds_keys.index(key)), shell.creds[key]["IP"], creduser, creddomain, credcred, credtype))
                    break

    shell.print_plain("")

def condense_creds(shell):
    bad_keys = []
    for key in shell.creds_keys:
        if shell.creds[key]["Username"] == "(null)":
            bad_keys.append(key)

    if bad_keys:
        new_creds = dict(shell.creds)
        for key in bad_keys:
            del new_creds[key]
            shell.creds_keys.remove(key)
        shell.creds = new_creds

def export_creds(shell):
    import json
    exportjson = open('/tmp/creds.json', 'w')
    exporttxt = open('/tmp/creds.txt', 'w')

    json_dict = {}

    for index, key in enumerate(shell.creds_keys):
        json_dict[str(index)] = shell.creds[key]
        exporttxt.write("IP: "+shell.creds[key]["IP"]+" "+" ".join(shell.creds[key]["Extra"]["IP"])+"\n")
        exporttxt.write("USERNAME: "+shell.creds[key]["Username"]+"\n")
        exporttxt.write("DOMAIN: "+shell.creds[key]["Domain"]+"\n")
        exporttxt.write("PASSWORD: "+shell.creds[key]["Password"]+" "+" ".join(shell.creds[key]["Extra"]["Password"])+"\n")
        exporttxt.write("NTLM: "+shell.creds[key]["NTLM"]+" "+" ".join(shell.creds[key]["Extra"]["NTLM"])+"\n")
        exporttxt.write("LM: "+shell.creds[key]["LM"]+" "+" ".join(shell.creds[key]["Extra"]["LM"])+"\n")
        exporttxt.write("SHA1: "+shell.creds[key]["SHA1"]+" "+" ".join(shell.creds[key]["Extra"]["SHA1"])+"\n")
        exporttxt.write("DCC: "+shell.creds[key]["DCC"]+" "+" ".join(shell.creds[key]["Extra"]["DCC"])+"\n")
        exporttxt.write("DPAPI: "+shell.creds[key]["DPAPI"]+" "+" ".join(shell.creds[key]["Extra"]["DPAPI"])+"\n")
        exporttxt.write("\n")

    exportjson.write(json.dumps(json_dict) + "\n")
    exporttxt.close()
    exportjson.close()
    shell.print_good("Credential store written to /tmp/creds.txt and /tmp/creds.json")

def creds_edit_shell(shell):
    old_prompt = shell.prompt
    old_clean_prompt = shell.clean_prompt

    shell.print_plain("Choose a Cred ID to edit. Type 'new' to add a credential. Type 'del' to delete a credential:")
    shell.prompt = "> "
    shell.clean_prompt = shell.prompt

    import os

    try:
        import readline
        readline.set_completer(None)
        option = creds_edit_shell_prompt(shell)

        try:
            int(option)
        except ValueError:
            if option.lower() != "new" and option.lower() != "del":
                shell.print_error("I don't understand")
                return

        if option.lower() == "new":
            shell.prompt = "new > "
            shell.clean_prompt = shell.prompt
            if shell.domain_info:
                shell.print_plain("Available Domains:")
                for domain in shell.domain_info:
                    shell.print_plain("\tFQDN: "+domain[0]+" | NetBIOS: "+domain[1])
                shell.print_plain("")

            shell.print_plain("Domain? (required)")
            domain = creds_edit_shell_prompt(shell)
            shell.print_plain("Username? (required)")
            user = creds_edit_shell_prompt(shell)
            new_key = (domain.lower(), user.lower())
            if new_key in shell.creds_keys:
                shell.print_error("User already in creds")
                return
            shell.creds_keys.append(new_key)
            shell.print_plain("Password?")
            password = creds_edit_shell_prompt(shell)
            shell.print_plain("NTLM?")
            ntlm = creds_edit_shell_prompt(shell)
            shell.print_plain("LM?")
            lm = creds_edit_shell_prompt(shell)
            shell.print_plain("SHA1?")
            sha1 = creds_edit_shell_prompt(shell)
            shell.print_plain("DCC?")
            dcc = creds_edit_shell_prompt(shell)
            shell.print_plain("DPAPI?")
            dpapi = creds_edit_shell_prompt(shell)
            c = {}
            c["Username"] = user
            c["Domain"] = domain
            c["Password"] = password
            c["NTLM"] = ntlm
            c["LM"] = lm
            c["SHA1"] = sha1
            c["DCC"] = dcc
            c["DPAPI"] = dpapi
            c["IP"] = "Manually added"
            c["Extra"] = {}
            c["Extra"]["IP"] = []
            c["Extra"]["Password"] = []
            c["Extra"]["NTLM"] = []
            c["Extra"]["SHA1"] = []
            c["Extra"]["DCC"] = []
            c["Extra"]["DPAPI"] = []
            c["Extra"]["LM"] = []
            shell.creds[new_key] = c

        elif option.lower() == "del":
            shell.prompt = "del > "
            shell.clean_prompt = shell.prompt
            shell.print_plain("Which Cred ID do you want to delete?")
            cred = creds_edit_shell_prompt(shell)
            if int(cred) < len(shell.creds_keys) and int(cred) >= 0:
                key = shell.creds_keys[int(cred)]
                shell.print_plain("IP: "+shell.creds[key]["IP"])
                shell.print_plain("USERNAME: "+shell.creds[key]["Username"])
                shell.print_plain("DOMAIN: "+shell.creds[key]["Domain"])
                shell.print_plain("PASSWORD: "+shell.creds[key]["Password"])
                shell.print_plain("NTLM: "+shell.creds[key]["NTLM"])
                shell.print_plain("LM: "+shell.creds[key]["LM"])
                shell.print_plain("SHA1: "+shell.creds[key]["SHA1"])
                shell.print_plain("DCC: "+shell.creds[key]["DCC"])
                shell.print_plain("DPAPI: "+shell.creds[key]["DPAPI"])
                shell.print_plain("")

                shell.print_plain("Are you sure you want to delete these creds?")
                confirm = creds_edit_shell_prompt(shell)
                if confirm.lower() == "y":
                    del shell.creds[key]
                    shell.creds_keys.remove(key)
                else:
                    return



        elif int(option) < len(shell.creds_keys) and int(option) >= 0:
            cid = int(option)
            key = shell.creds_keys[cid]
            cred = shell.creds[key]
            shell.prompt = option+" > "
            shell.clean_prompt = shell.prompt

            shell.print_plain("IP: "+shell.creds[key]["IP"])
            shell.print_plain("USERNAME: "+shell.creds[key]["Username"])
            shell.print_plain("DOMAIN: "+shell.creds[key]["Domain"])
            shell.print_plain("PASSWORD: "+shell.creds[key]["Password"])
            shell.print_plain("NTLM: "+shell.creds[key]["NTLM"])
            shell.print_plain("LM: "+shell.creds[key]["LM"])
            shell.print_plain("SHA1: "+shell.creds[key]["SHA1"])
            shell.print_plain("DCC: "+shell.creds[key]["DCC"])
            shell.print_plain("DPAPI: "+shell.creds[key]["DPAPI"])
            shell.print_plain("")

            shell.print_plain("Which section would you like to edit?")
            option = creds_edit_shell_prompt(shell)
            if option.lower() in [k.lower() for k in shell.creds[key]]:
                for subkey in shell.creds[key]:
                    if option.lower() == subkey.lower():
                        break
                if subkey == "Username" or subkey == "Domain":
                    pass
                elif shell.creds[key]["Extra"][subkey]:
                    shell.print_plain("Extras\n------")
                    for item in shell.creds[key]["Extra"][subkey]:
                        shell.print_plain("  "+item)
                    shell.print_plain("")
                shell.print_plain("New value?")
                val = creds_edit_shell_prompt(shell)
                shell.print_plain("Are you sure you want to change the value to '"+val+"'?")
                confirm = creds_edit_shell_prompt(shell)
                if confirm.lower() == "y":
                    if subkey == "Username" or subkey == "Domain":
                        new_key_list = list(key)
                        if subkey == "Domain":
                            new_key_list[0] = val.lower()
                        else:
                            new_key_list[1] = val.lower()

                        new_key = tuple(new_key_list)

                        if new_key in shell.creds_keys:
                            shell.print_warning("There is already a credential with this key. Continuing will merge the creds. Continue?")
                            confirm = creds_edit_shell_prompt(shell)
                            if confirm.lower() == "y":
                                for k in shell.creds[key]:
                                    if k == "Username" or k == "Domain":
                                        continue
                                    if k == "Extra":
                                        for extra_key in shell.creds[key][k]:
                                            if not shell.creds[key][k][extra_key]:
                                                continue
                                            shell.creds[new_key][k][extra_key].append(shell.creds[key][k][extra_key])
                                            new_extras = []
                                            for item in shell.creds[new_key][k][extra_key]:
                                                if isinstance(item,str):
                                                    new_extras.append(item)
                                                else:
                                                    for subitem in item:
                                                        new_extras.append(subitem)
                                            shell.creds[new_key][k][extra_key] = new_extras
                                            shell.creds[new_key][k][extra_key] = list(set(shell.creds[new_key][k][extra_key]))
                                        continue

                                    match_val = shell.creds[key][k]
                                    orig_val = shell.creds[new_key][k]
                                    if match_val and not orig_val:
                                        # if its not in the original, then we're gonna add it
                                        shell.creds[new_key][k] = match_val
                                    if match_val and orig_val and match_val != orig_val:
                                        # if we have values for both and they're not the same, add to the originals extras
                                        shell.creds[new_key]["Extra"][k].append(match_val)
                                        # remove the duplicates
                                        shell.creds[new_key]["Extra"][k] = list(set(shell.creds[new_key]["Extra"][k]))
                                del shell.creds[key]
                                shell.creds_keys.remove(key)


                        else:
                            shell.creds[new_key] = shell.creds.pop(key)
                            shell.creds_keys[cid] = new_key
                            shell.creds[new_key][subkey] = val
                        return


                    if val in shell.creds[key]["Extra"][subkey]:
                        shell.creds[key]["Extra"][subkey].remove(val)

                    if shell.creds[key][subkey]:
                        shell.creds[key]["Extra"][subkey].append(shell.creds[key][subkey])
                    shell.creds[key][subkey] = val
                else:
                    return

            else:
                shell.print_error("Not a real section")
                return

        else:
            shell.print_error("Not a valid Cred ID")
            return

        shell.update_restore = True



    except KeyboardInterrupt:
        shell.print_plain(shell.clean_prompt)
        return
    finally:
        shell.prompt = old_prompt
        shell.clean_prompt = old_clean_prompt

def creds_edit_shell_prompt(shell):
    import os
    val = shell.get_command(shell.prompt)

    if shell.spool:
        shell.spool_log(shell.prompt, val)

    return val


def execute(shell, cmd):
    condense_creds(shell)

    splitted = cmd.split()

    if len(splitted) > 1:
        if splitted[1] == "-a":
            print_creds_detailed(shell)
        elif splitted[1] == "-u":
            if len(splitted) < 3:
                shell.print_error("Need to provide a username or a Cred ID!")
            elif len(splitted) == 4 and "--like" == splitted[-1]:
                print_creds_detailed(shell, splitted[2], True)
            else:
                print_creds_detailed(shell, splitted[2])
        elif splitted[1] == "-x":
            export_creds(shell)
        elif splitted[1] == "-d":
            if shell.domain_info:
                if len(splitted) < 3:
                    shell.print_good("Gathered domains")
                    for d in shell.domain_info:
                        shell.print_plain("\tLong: "+d[0]+", Short: "+d[1])
                else:
                    print_creds_das(shell, splitted[2])
            else:
                shell.print_error("No domain information gathered. Please run implant/gather/enum_domain_info.")

        elif splitted[1] == "--sort":
            if len(splitted) < 3:
                shell.print_error("Need to provide a column name to sort on!")
            else:
                print_creds(shell, splitted[2])

        elif splitted[1] == "--edit":
            creds_edit_shell(shell)

        elif splitted[1] == "-D":
            if len(splitted) < 3:
                shell.print_error("Need to provide a domain")
            else:
                print_creds(shell, "Normal", splitted[2])

        elif splitted[1] == "--search":
            if len(splitted) < 3:
                shell.print_error("Need to provide text to search for")
            else:
                print_creds(shell, "Normal", "", splitted[2])

        else:
            shell.print_error("Unknown option '"+splitted[1]+"'")
    else:
        if shell.creds:
            print_creds(shell)
        else:
            shell.print_error("No credentials have been gathered yet")
