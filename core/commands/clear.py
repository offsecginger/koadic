DESCRIPTION = "clear the screen"

def autocomplete(shell, line, text, state):
    return None

def help(shell):
    pass

def execute(shell, cmd):
    print("\x1b[2J\x1b[H")
