DESCRIPTION = "Love is in the wire"

def autocomplete(shell, line, text, state):
    return None

def help(shell):
    pass

def execute(shell, cmd):

    print(open("data/valentine.txt", "rb").read().decode("unicode_escape"))
