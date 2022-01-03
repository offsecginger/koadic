DESCRIPTION = "kill a zombie by ID"

def autocomplete(shell, line, text, state):
    pass

def help(shell):
    shell.print_plain("")
    shell.print_plain("Usage: kill #")
    shell.print_plain("       kill all")
    shell.print_plain("       kill dead")
    shell.print_plain("")

def kill_zombie(shell, id):
    formats = "\t{0:<5}{1:<10}{2:<20}{3:<40}"

    if not id.isdigit() and id.lower() not in ["all", "dead"]:
        shell.print_error("Not a valid argument to kill: %s" % id)
        return

    if id.lower() == "all":
        [session.kill() for skey, session in shell.sessions.items() if session.killed == False]

    elif id.lower() == "dead":
        [session.kill() for skey, session in shell.sessions.items() if session.status == 0 and session.killed == False]

    else:
        [session.kill() for skey, session in shell.sessions.items() if session.id == int(id) and session.killed == False]

    if id.lower() == "all":
        shell.print_good("All Zombies Killed!")
    elif id.lower() == "dead":
        shell.print_good("Dead Zombies Killed!")

    shell.play_sound('KILL')

def execute(shell, cmd):

    splitted = cmd.split()

    if len(splitted) > 1:
        id = splitted[1]
        kill_zombie(shell, id)
        return

    help(shell)
