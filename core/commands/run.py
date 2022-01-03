DESCRIPTION = "runs the current module"

def autocomplete(shell, line, text, state):
    return None

def help(shell):
    pass

def execute(shell, cmd):
    try:
        env = shell.plugins[shell.state]
        env.run()
    except KeyboardInterrupt:
        return
