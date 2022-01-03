DESCRIPTION = "It's paddy, not patty"

def autocomplete(shell, line, text, state):
    return None

def help(shell):
    pass

def execute(shell, cmd):

    print(open("data/shamrock.txt", "rb").read().decode("unicode_escape"))
