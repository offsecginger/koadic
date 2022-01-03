DESCRIPTION = "shows the current module options"

def autocomplete(shell, line, text, state):
    return None

def help(shell):
    shell.print_plain("")
    shell.print_plain("Use %s for advanced options" % (shell.colors.colorize("info -a", shell.colors.BOLD)))
    shell.print_plain("")

def execute(shell, cmd):
    env = shell.plugins[shell.state]

    # dynamically set format length
    maxlen = 0
    for option in env.options.options:
        if option.advanced and " -a" not in cmd:
            continue

        if option.hidden:
            continue

        if len(option.name) > maxlen: maxlen = len(option.name)

    formats = '\t{{0:<{0}}}{{1:<20}}{{2:<8}}{{3:<16}}'.format(maxlen+3)

    shell.print_plain("")
    shell.print_plain(formats.format("NAME", "VALUE", "REQ", "DESCRIPTION"))
    shell.print_plain(formats.format("-----","------------", "----", "-------------"))

    for option in env.options.options:
        if option.advanced and " -a" not in cmd:
            continue

        if option.hidden:
            continue

        prettybool = "yes" if option.required else "no"
        value = str(option.value)[0:16] + "..." if len(str(option.value)) > 16 else str(option.value)
        shell.print_plain(formats.format(option.name, value, prettybool, option.description))

    shell.print_plain("")
