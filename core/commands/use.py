DESCRIPTION = "switch to a different module"

def autocomplete(shell, line, text, state):
    import readline
    everything = readline.get_line_buffer()
    cursor_idx = readline.get_begidx()
    idx = 0
    for chunk in everything.split(" "):
        fulltext = chunk
        idx += len(chunk) + 1
        if idx > cursor_idx:
            break
    prefix, suffix = fulltext.rsplit("/",maxsplit=1) if "/" in fulltext else ("",fulltext)
    if prefix:
        prefix += "/"

    options = []
    tmp = list(shell.plugins.keys())
    for plugin in shell.plugins:
        tmp.append(plugin.split("/")[-1])
    for plugin in tmp:
        if not plugin.startswith(fulltext):
            continue
        chunk = plugin[len(prefix):]
        if "/" in chunk:
            options.append(chunk.split("/")[0]+"/")
        else:
            options.append(chunk+" ")
    options = list(sorted(set(options)))
    try:
        return options[state]
    except:
        return None

def help(shell):
    pass

def execute(shell, cmd):
    splitted = cmd.split()

    if len(splitted) > 1:
        module = splitted[1]
        if "/" not in module:
            module = [k for k in shell.plugins if k.lower().split('/')[-1] == module.lower()][0]
        if module not in shell.plugins:
            shell.print_error("No module named %s" % (module))
            return

        shell.previous = shell.state
        shell.state = module
