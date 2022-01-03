DESCRIPTION = "go back to the last used module"

def autocomplete(shell, line, text, state):
    pass

def help(shell):
    pass

def execute(shell, cmd):
    tmp = shell.state
    try:
        shell.state = shell.previous
    except:
        pass
    shell.previous = tmp

