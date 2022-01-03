import core.stager

DESCRIPTION = "creates a stager for the current module"

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
    else:
        prefix, suffix = fulltext.rsplit("=",maxsplit=1) if "=" in fulltext else ("",fulltext)
        if prefix:
            prefix += "="

    options = []

    tmp = [plugin for plugin in list(shell.plugins.keys()) if plugin.split("/")[0].lower() == "stager"]
    for plugin in shell.plugins:
        if plugin.split("/")[0].lower() == "stager":
            tmp.append(plugin.split("/")[-1])

    if len(line.split()) > 1 and line.split()[1] in tmp:
        stager = line.split()[1]
        if "/" not in stager:
            try:
                stager = [k for k in shell.plugins if k.lower().split('/')[-1] == stager.lower()][0]
            except IndexError:
                shell.print_error("No stager named %s" % (stager))
                return
        plugin = shell.plugins[stager]
        options = [x.name + "=" for x in plugin.options.options if x.name.upper().startswith(fulltext.split("=")[0].upper()) and not x.hidden]
        options += [x.alias + "=" for x in plugin.options.options if x.alias.upper().startswith(fulltext.upper()) and not x.hidden and x.alias]
        if prefix.endswith("="):
            option = [x for x in plugin.options.options if x.name.upper()+"=" == prefix.upper() or x.alias.upper()+"=" == prefix.upper()[0]][0]
            options = []
            if option.boolean:
                options = [prefix+x for x in ['true', 'false'] if x.upper().startswith(fulltext.split("=")[1].upper())]
            if option.file:
                options = filepaths(fulltext.split("=")[1])
            if option.implant:
                pass
            if option.enum:
                options = [prefix+x for x in option.enum if x.upper().startswith(fulltext.split("=")[1].upper())]
            if options:
                return options[state]


        try:
            return options[state]
        except:
            return None


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
    shell.print_plain("")
    shell.print_plain("createstager [STAGER_TYPE] [OPTION1=VAL1 OPTION2=VAL2]")
    shell.print_plain("")
    shell.print_plain("STAGER_TYPE defaults to stager/js/mshta if not defined")
    shell.print_plain("Options default to ONESHOT = true, MODULE = the current module and ENDPOINT = 5 random characters")
    shell.print_plain("Tab-completion available!")
    shell.print_plain("")

def save_options(plugin):
    import copy
    old_options = copy.deepcopy(plugin.options)
    return old_options

def restore_options(plugin, options):
    plugin.options = options

def execute(shell, cmd):
    splitted = cmd.split()

    if len(splitted) > 1:
        stager = splitted[1]
        if "/" not in stager:
            try:
                stager = [k for k in shell.plugins if k.lower().split('/')[-1] == stager.lower()][0]
            except IndexError:
                shell.print_error("No stager named %s" % (stager))
                return
            
        if stager.split("/")[0].lower() != "stager":
            shell.print_error("createstager needs a stager... DUH! This isn't a stager: %s" % (stager))
            return

        plugin = shell.plugins[stager]
        old_options = save_options(plugin)
        plugin.options.set("MODULE", shell.state)
        plugin.options.set("ONESHOT", "true")
        import random, string
        plugin.options.set("ENDPOINT", ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for n in range(5)))

        if len(splitted) > 2:
            for o in splitted[2:]:
                if "=" not in o:
                    shell.print_error("Malformed option: %s" % (o))
                    return
                option, value = o.split("=")
                if option.upper() not in [n.upper() for option in plugin.options.options for n in [option.name, option.alias] if n]:
                    shell.print_error("Fake option: %s" % (option))
                    return

                if not plugin.options.set(option, value):
                    shell.print_error("'%s' is not a valid value for option '%s'" % (value, option))
                    return

    else:
        plugin = shell.plugins["stager/js/mshta"]
        old_options = save_options(plugin)
        plugin.options.set("MODULE", shell.state)
        plugin.options.set("ONESHOT", "true")
        import random, string
        plugin.options.set("ENDPOINT", ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for n in range(5)))

    shell.print_status(f"Creating a stager for {shell.state}...")
    plugin.run()
    restore_options(plugin, old_options)
