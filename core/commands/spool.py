import os

DESCRIPTION = "write output to a file"

def autocomplete(shell, line, text, state):
    options = filepaths(text)
    return options[state]

def help(shell):
    shell.print_plain("")
    shell.print_plain("Use %s to spool to /tmp/koadic.spool" % (shell.colors.colorize("spool on", shell.colors.BOLD)))
    shell.print_plain("Use %s to spool to a defined file" % (shell.colors.colorize("spool FILEPATH", shell.colors.BOLD)))
    shell.print_plain("Use %s to stop spooling" % (shell.colors.colorize("spool off", shell.colors.BOLD)))
    shell.print_plain("")

def filepaths(text):
    import readline
    everything = readline.get_line_buffer()
    cursor_idx = readline.get_begidx()
    idx = 0
    for chunk in everything.split(" "):
        fullpath = chunk
        idx += len(chunk) + 1
        if idx > cursor_idx:
            break

    if os.path.isfile(fullpath):
        return None
    if "/" in fullpath:
        d = os.path.dirname(fullpath)
    else:
        d = "."

    res = []
    for candidate in os.listdir(d):
        if not candidate.startswith(text):
            continue
        if os.path.isdir(d+os.path.sep+candidate):
            res.append(candidate + os.path.sep)
        else:
            res.append(candidate + " ")
    return res

def execute(shell, cmd):

    splitted = cmd.split()

    if len(splitted) > 1:
        option = splitted[1]
        if option == 'on':
            shell.spool = '/tmp/koadic.spool'
            shell.print_status("Spooling to /tmp/koadic.spool...")
        elif option == 'off':
            if shell.spool:
                shell.spool = False
                shell.print_status("Spooling stopped...")
        else:
            shell.spool = option
            shell.print_status("Spooling to "+option+"...")
    else:
        help(shell)
