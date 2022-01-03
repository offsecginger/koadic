DESCRIPTION = "taco time"

def autocomplete(shell, line, text, state):
    return None

def help(shell):
    pass

def execute(shell, cmd):

    print(open("data/taco.txt", "rb").read().decode("unicode_escape"))
