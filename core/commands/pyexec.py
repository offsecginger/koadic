DESCRIPTION = "evals some python"

def autocomplete(shell, line, text, state):
    return None

def help(shell):
    pass

def execute(shell, cmd):
    code = " ".join(cmd.split(" ")[1:])
    exec(code)
