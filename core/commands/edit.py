DESCRIPTION = "shell out to an editor for the current module"

def autocomplete(shell, line, text, state):
    return None

def help(shell):
    shell.print_plain("")
    shell.print_plain("Use %s to edit the current module's python file" % (shell.colors.colorize("edit / edit py / edit python", shell.colors.BOLD)))
    shell.print_plain("Use %s to edit the current module's associated javascript file (if applicable)" % (shell.colors.colorize("edit js / edit javascript", shell.colors.BOLD)))
    shell.print_plain("Use %s to edit the current module's associated vbscript file (if applicable)" % (shell.colors.colorize("edit vbs / edit vbscript", shell.colors.BOLD)))
    shell.print_plain("")
    shell.print_plain("NOTE: Uses $EDITOR env variable, otherwise will fallback to vi.")
    shell.print_plain("")

def execute(shell, cmd):
    import subprocess, os

    try:
        if not os.environ['EDITOR']:
            shell.print_error("$EDITOR env variable not set, falling back to vi!")
            editor = 'vi'
        else:
            editor = os.environ['EDITOR']
    except KeyError:
        shell.print_error("$EDITOR env variable does not exist, falling back to vi!")
        editor = 'vi'

    py_file = "modules/"+shell.state+".py"
    js_file = "data/"+shell.state+".js"
    vbs_file = "data/"+shell.state+".vbs"
    dropper_file = "data/"+shell.state+".dropper"

    splitted = cmd.split()

    if len(splitted) > 1:
        ftype = splitted[1].lower()
        if ftype == "py" or ftype == "python":
            file = py_file
        elif ftype == "js" or ftype == "javascript":
            file = js_file
        elif ftype == "vbs" or ftype == "vbscript":
            file = vbs_file
        elif ftype == "dropper":
            file = dropper_file
        else:
            return

        if os.path.isfile(file):
            editcmd = [editor, file]
        else:
            return
    else:
        editcmd = [editor, py_file]
    
    subprocess.call(editcmd)
    shell.run_command('load')
