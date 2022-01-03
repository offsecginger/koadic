DESCRIPTION = "shows collected domain information"

def autocomplete(shell, line, text, state):
    options = [x + " " for y in shell.domain_info for x in y if x.upper().startswith(text.upper())]
    try:
        return options[state]
    except:
        return None

def help(shell):
    shell.print_plain("")
    shell.print_plain("Use %s for a useful overview of gathered domain details" % (shell.colors.colorize("domain DOMAIN", shell.colors.BOLD)))
    shell.print_plain("Use %s for full domain details" % (shell.colors.colorize("domain -a DOMAIN", shell.colors.BOLD)))
    shell.print_plain("Use %s for domain admins" % (shell.colors.colorize("domain -d DOMAIN", shell.colors.BOLD)))
    shell.print_plain("Use %s for domain users" % (shell.colors.colorize("domain -u DOMAIN", shell.colors.BOLD)))
    shell.print_plain("Use %s for domain password policy" % (shell.colors.colorize("domain -p DOMAIN", shell.colors.BOLD)))
    shell.print_plain("Use %s for domain controllers" % (shell.colors.colorize("domain -c DOMAIN", shell.colors.BOLD)))
    shell.print_plain("Use %s for domain computers" % (shell.colors.colorize("domain -m DOMAIN", shell.colors.BOLD)))
    shell.print_plain("Use %s to run implant/gather/enum_domain_info on a zombie" % (shell.colors.colorize("domain -z ZOMBIE_ID", shell.colors.BOLD)))
    shell.print_plain("Use %s to export domain information" % (shell.colors.colorize("domain -x [DOMAIN]", shell.colors.BOLD)))
    shell.print_plain("")

def print_domains(shell):
    shell.print_plain("")
    shell.print_plain("Available Domains:")
    for domain in shell.domain_info:
        shell.print_plain("\tFQDN: "+domain[0]+" | NetBIOS: "+domain[1])
    shell.print_plain("")

def print_domain_detailed(shell, domain_key):
    print_domain_admins(shell, domain_key)
    print_domain_users(shell, domain_key)
    print_domain_password_policy(shell, domain_key)
    print_domain_controllers(shell, domain_key)
    print_domain_computers(shell, domain_key)

def print_domain_admins(shell, domain_key):
    if not "Domain Admins" in shell.domain_info[domain_key]:
        shell.print_error("Domain Admins not gathered for target domain. Please run implant/gather/enum_domain_info")
        return

    das = list(shell.domain_info[domain_key]["Domain Admins"])

    max_len = len(sorted(das, key=len)[-1])+8
    formats = "{{0:{0}}}{{1:{0}}}{{2:{0}}}{{3:{0}}}".format(max_len) # does this make me an idiot or a genius?

    for da in das:
        c_key = ""
        if (domain_key[0], da) in shell.creds_keys:
            c_key = (domain_key[0], da)
        elif (domain_key[1], da) in shell.creds_keys:
            c_key = (domain_key[1], da)

        if c_key and (shell.creds[c_key]["Password"] or shell.creds[c_key]["NTLM"] or shell.creds[c_key]["LM"] or shell.creds[c_key]["SHA1"] or shell.creds[c_key]["DCC"] or shell.creds[c_key]["DPAPI"]):
            loc = das.index(da)
            das[loc] = da+"*"

    shell.print_plain("")
    shell.print_plain("Domain Admins")
    shell.print_plain("-------------")
    for da_row in [das[x:x+4] for x in range(0, len(das), 4)]:
        for i in range(0, 4-len(da_row)):
            da_row.append("")
        shell.print_plain(formats.format(da_row[0], da_row[1], da_row[2], da_row[3]))

    shell.print_plain("")
    shell.print_plain("* = credentials in cred store")
    shell.print_plain("")

def print_domain_users(shell, domain_key):
    if not "Domain Users" in shell.domain_info[domain_key]:
        shell.print_error("Domain Users not gathered for target domain. Please run implant/gather/enum_domain_info")
        return

    users = shell.domain_info[domain_key]["Domain Users"]

    max_len = len(sorted(users, key=len)[-1])+8
    formats = "{{0:{0}}}{{1:{0}}}{{2:{0}}}{{3:{0}}}".format(max_len) # does this make me an idiot or a genius?

    for user in users:
        c_key = ""
        if (domain_key[0], user) in shell.creds_keys:
            c_key = (domain_key[0], user)
        elif (domain_key[1], user) in shell.creds_keys:
            c_key = (domain_key[1], user)

        if c_key and (shell.creds[c_key]["Password"] or shell.creds[c_key]["NTLM"]):
            loc = users.index(user)
            users[loc] = user+"*"

    shell.print_plain("")
    shell.print_plain("Domain Users")
    shell.print_plain("-------------")
    for user_row in [users[x:x+4] for x in range(0, len(users), 4)]:
        for i in range(0, 4-len(user_row)):
            user_row.append("")
        shell.print_plain(formats.format(user_row[0], user_row[1], user_row[2], user_row[3]))

    shell.print_plain("")
    shell.print_plain("* = credentials in cred store")
    shell.print_plain("")

def print_domain_password_policy(shell, domain_key):
    if not "Password Policy" in shell.domain_info[domain_key]:
        shell.print_error("Password Policy not gathered for target domain. Please run implant/gather/enum_domain_info")
        return

    shell.print_plain("")
    shell.print_plain("Password Policy")
    policy_string =  "\tForce user logoff how long after time expires?:       %s\n"
    policy_string += "\tMinimum password age (days):                          %s\n"
    policy_string += "\tMaximum password age (days):                          %s\n"
    policy_string += "\tMinimum password length:                              %s\n"
    policy_string += "\tLength of password history maintained:                %s\n"
    policy_string += "\tLockout threshold:                                    %s\n"
    policy_string += "\tLockout duration (minutes):                           %s\n"
    policy_string += "\tLockout observation window (minutes):                 %s\n"
    policy_string = policy_string % tuple(shell.domain_info[domain_key]["Password Policy"])

    shell.print_plain(policy_string)

    shell.print_plain("")

def print_domain_controllers(shell, domain_key):
    if not "Domain Controllers" in shell.domain_info[domain_key]:
        shell.print_error("Domain Controllers not gathered for target domain. Please run implant/gather/enum_domain_info")
        return

    shell.print_plain("")
    shell.print_plain("Domain Controllers")
    for dc in shell.domain_info[domain_key]["Domain Controllers"]:
        shell.print_plain("\tDC: "+dc[0]+" ("+dc[1]+")")

    shell.print_plain("")

def print_domain_computers(shell, domain_key):
    if not "Domain Computers" in shell.domain_info[domain_key]:
        shell.print_error("Domain Computers not gathered for target domain. Please run implant/gather/enum_domain_info")
        return

    shell.print_plain("")
    shell.print_plain("Domain Computers")
    shell.print_plain("----------------")
    for computer in shell.domain_info[domain_key]["Domain Computers"]:
        shell.print_plain(computer[0]+" ("+computer[1]+")")

    shell.print_plain("")


def print_opti_info(shell, domain):

    domains = [j for i in shell.domain_info for j in i]
    if not domain.lower() in domains:
        shell.print_error("Supplied domain not known")
        return
    domain_key = [i for i in shell.domain_info if domain.lower() in i][0]

    if "Domain Admins" in shell.domain_info[domain_key]:
        print_domain_admins(shell, domain_key)

    if "Domain Controllers" in shell.domain_info[domain_key]:
        print_domain_controllers(shell, domain_key)

    shell.print_plain("Information gathered for domain "+str(domain_key)+":")
    for h in shell.domain_info[domain_key]:
        shell.print_plain("\t"+h)
    shell.print_plain("")
    shell.print_plain("See 'help domain' to access full details.")
    shell.print_plain("")



def export_domain_info(shell, domain_key="*"):
    if domain_key == "*":
        export = open('/tmp/domain_info.txt', 'w')
        keys = list(shell.domain_info.keys())
    else:
        export = open('/tmp/'+domain_key[0]+'_domain_info.txt', 'w')
        keys = [domain_key]

    for key in keys:
        export.write(str(key)+"\n")
        for subkey in shell.domain_info[key]:
            export.write(str(key)+"-"+subkey+"\n")
            for value in shell.domain_info[key][subkey]:
                export.write(str(value)+"\n")
            export.write("/"+str(key)+"-"+subkey+"\n")
        export.write("/"+str(key)+"\n")

    shell.print_good("Domain info written to "+export.name)
    export.close()

def execute(shell, cmd):
    splitted = cmd.split()

    if len(splitted) > 1 and splitted[1] == "-z":
        if len(splitted) < 3:
            shell.print_error("Need to provide a zombie ID!")
            return
        plugin = shell.plugins["implant/gather/enum_domain_info"]
        old_zombie = plugin.options.get("ZOMBIE")
        plugin.options.set("ZOMBIE", splitted[2])
        plugin.run()
        plugin.options.set("ZOMBIE", old_zombie)
        return

    if shell.domain_info:
        if len(splitted) > 2:
            domain = splitted[2]
            domains = [j for i in shell.domain_info for j in i]
            if not domain.lower() in domains:
                shell.print_error("Supplied domain not known")
                return
            domain_key = [i for i in shell.domain_info if domain.lower() in i][0]

            if splitted[1] == "-a":
                print_domain_detailed(shell, domain_key)
            elif splitted[1] == "-d":
                print_domain_admins(shell, domain_key)
            elif splitted[1] == "-u":
                print_domain_users(shell, domain_key)
            elif splitted[1] == "-p":
                print_domain_password_policy(shell, domain_key)
            elif splitted[1] == "-c":
                print_domain_controllers(shell, domain_key)
            elif splitted[1] == "-m":
                print_domain_computers(shell, domain_key)
            elif splitted[1] == "-x":
                export_domain_info(shell, domain_key)
            else:
                shell.print_error("Unknown option '"+splitted[1]+"'")
        elif len(splitted) > 1 and splitted[1] == "-x":
            export_domain_info(shell)
        elif len(splitted) > 1:
            print_opti_info(shell, splitted[1])
        else:
            print_domains(shell)
    else:
        shell.print_error("No domain information gathered. Please run implant/gather/enum_domain_info.")
