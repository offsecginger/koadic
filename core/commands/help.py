DESCRIPTION = "displays help info for a command"


def autocomplete(shell, line, text, state):

    # should never go this big...
    if len(line.split()) > 2:
        return None

    options = [x + " " for x in shell.actions if x.startswith(text)]

    try:
        return options[state]
    except:
        return None


def help(shell):
    shell.print_plain("")
    shell.print_plain("You definitely need help")
    shell.print_plain("")

def execute(shell, cmd):

    splitted = cmd.split()

    if len(splitted) == 1:
        return help_all(shell)

    if len(splitted) > 1:
        return help_command(shell, splitted[1])


def help_command(shell, command):
    if command not in shell.actions:
        shell.print_error("No command named %s" % command)
        return

    shell.actions[command].help(shell)


def help_all(shell):
    formats = '\t{0:<14}{1:<16}'

    shell.print_plain("")
    shell.print_plain(formats.format("COMMAND", "DESCRIPTION"))
    shell.print_plain(formats.format("---------", "-------------"))

    for key, env in sorted(shell.actions.items()):
        if getattr(env, "hidden_command", False):
            continue
        shell.print_plain(formats.format(key, env.DESCRIPTION))

    shell.print_plain("")
    shell.print_plain('Use "help %s" to find more info about a command.' %
                      shell.colors.colorize("command", [shell.colors.BOLD]))
    shell.print_plain("")
