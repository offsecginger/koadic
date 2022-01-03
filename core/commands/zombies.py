import datetime
import core.session

DESCRIPTION = "lists hooked targets"

def autocomplete(shell, line, text, state):
    return None

def help(shell):
    pass

def execute(shell, cmd):
    splitted = cmd.split()
    all_sessions = [session for skey, session in shell.sessions.items()]
    all_sessions.sort(key=lambda s: s.id)


    if len(splitted) == 1:
        cur_sessions = []
        for session in all_sessions:
            if not session.killed:
                cur_sessions.append(session)
        print_all_sessions(shell, cur_sessions)
        return

    # Zombie details for killed zombies
    if splitted[1] == "killed":
        cur_sessions = []
        for session in all_sessions:
            if session.killed:
                cur_sessions.append(session)

        if len(cur_sessions) == 1:
            print_session(shell, cur_sessions[0])
            return
        elif len(cur_sessions) > 1:
            print_all_sessions(shell, cur_sessions)
            return

    # Zombie details by IP
    if len(splitted[1].split(".")) == 4:
        cur_sessions = []
        for session in all_sessions:
            if session.ip == splitted[1] and not session.killed:
                cur_sessions.append(session)
        # If there's only one session, we want to show it
        if len(cur_sessions) == 1:
            print_session(shell, cur_sessions[0])
            return
        elif len(cur_sessions) > 1:
            print_all_sessions(shell, cur_sessions)
            return

    # Zombie details by Domain
    domains = [j for i in shell.domain_info for j in i]
    if splitted[1].lower() in domains:
        domain_key = [i for i in shell.domain_info if splitted[1].lower() in i][0]
        alt_domain = [i for i in domain_key if i != splitted[1].lower()][0]
        cur_sessions = []
        for session in all_sessions:
            d = session.domain.lower()
            if (d == splitted[1].lower() or d == alt_domain.lower()) and not session.killed:
                cur_sessions.append(session)

        if len(cur_sessions) == 1:
            print_session(shell, cur_sessions[0])
            return
        elif len(cur_sessions) > 1:
            print_all_sessions(shell, cur_sessions)
            return

    # Zombie details by ID
    try:
        for session in all_sessions:
            if session.id == int(splitted[1]):
                print_session(shell, session)
                return
    except ValueError:
        shell.print_error("Expected int or valid ip/domain")

    shell.print_error("Unable to find that session.")

def print_data(shell, title, data):
    formats = "\t{0:<32}{1:<32}"
    shell.print_plain(formats.format(shell.colors.colorize(title + ":", [shell.colors.BOLD]), data))

def print_jobs(shell, session):

    formats = "\t{0:<5}{1:<32}{2:<10}{3:<8}"
    shell.print_plain(formats.format("JOB", "NAME", "STATUS", "ERRNO"))
    shell.print_plain(formats.format("----", "---------", "-------", "-------"))

    for job in [j for jkey, j in shell.jobs.items() if session.id == j.session_id]:
        last = job.name.split("/")[-1]
        jobname = [n[0:3] for n in job.name.split("/")[:-1]]
        jobname.append(last)
        jobname = "/".join(jobname)
        shell.print_plain(formats.format(job.id, jobname, job.status_string(), job.errno))


def print_session(shell, session):
    shell.print_plain("")
    print_data(shell, "ID", session.id)
    print_data(shell, "Status", "Alive" if session.status == core.session.Session.ALIVE else "Dead")
    print_data(shell, "First Seen", datetime.datetime.fromtimestamp(session.first_seen).strftime('%Y-%m-%d %H:%M:%S'))
    print_data(shell, "Last Seen", datetime.datetime.fromtimestamp(session.last_active).strftime('%Y-%m-%d %H:%M:%S'))
    if session.ip != session.origin_ip:
        print_data(shell, "Staged From", session.origin_ip)
    print_data(shell, "Listener", session.stager.payload.id)
    shell.print_plain("")
    print_data(shell, "IP", session.ip)
    print_data(shell, "User", session.user)
    print_data(shell, "Hostname", session.computer)
    print_data(shell, "Primary DC", session.dc)
    print_data(shell, "OS", session.os)
    print_data(shell, "OSBuild", session.build)
    print_data(shell, "OSArch", session.arch)
    print_data(shell, "Elevated", "YES!" if session.elevated == core.session.Session.ELEVATED_TRUE else "No")
    shell.print_plain("")
    print_data(shell, "User Agent", session.user_agent)
    print_data(shell, "Session Key", session.key)
    shell.print_plain("")
    print_jobs(shell, session)
    shell.print_plain("")

def print_all_sessions(shell, all_sessions):
    formats = "\t{0:<5}{1:<16}{2:<8}{3:16}"

    shell.print_plain("")

    shell.print_plain(formats.format("ID", "IP", "STATUS", "LAST SEEN"))
    shell.print_plain(formats.format("---", "---------", "-------", "------------"))
    for session in all_sessions:
        alive = "Alive" if session.status == 1 else "Dead"
        seen = datetime.datetime.fromtimestamp(session.last_active).strftime('%Y-%m-%d %H:%M:%S')
        elevated = '*' if session.elevated == core.session.Session.ELEVATED_TRUE else ''
        shell.print_plain(formats.format(str(session.id)+elevated, session.ip, alive, seen))

    shell.print_plain("")
    shell.print_plain('Use "zombies %s" for detailed information about a session.' % shell.colors.colorize("ID", [shell.colors.BOLD]))
    shell.print_plain('Use "zombies %s" for sessions on a particular host.' % shell.colors.colorize("IP", [shell.colors.BOLD]))
    shell.print_plain('Use "zombies %s" for sessions on a particular Windows domain.' % shell.colors.colorize("DOMAIN", [shell.colors.BOLD]))
    shell.print_plain('Use "zombies killed" for sessions that have been manually killed.')
    shell.print_plain("")
