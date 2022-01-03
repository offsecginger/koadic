DESCRIPTION = "turn sounds off/on: sound(0|1)"

def autocomplete(shell, line, text, state):
    return None

def help(shell):
    pass

def execute(shell, cmd):
    try:
        import playsound
    except:
        shell.print_error('You do not have the playsound module installed. Please run \'pip install playsound\' to enable this feature!')
        return

    splitted = cmd.split()

    if len(splitted) > 1:
        sw = splitted[1].lower()
        if sw == "1" or sw == "true" or sw == "on":
            from core.sounds import sounds
            shell.sounds = sounds
            shell.play_sound('ON')
        else:
            shell.sounds = {}

    shell.print_status("Sounds: %s" % ("On" if shell.sounds else "Off"))
