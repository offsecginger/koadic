DESCRIPTION = "stub command for help text"
hidden_command = True

def autocomplete(shell, line, text, state):
    return None

def help(shell):
    msg = """
Unlike most connectback RATs, Koadic does not rely on a single long-lived TCP connection. Windows Script Host isn't smart enough to do that. Instead, Koadic uses repeated HTTP requests in separate connections. It is important that you not modify the URL of a listener between when Koadic spits it out and when it is executed on the host because the very first thing Koadic is going to try and do after the first connection is establish a second connection - and it's going to try and make the second connection using the URL Koadic knows about, not the one you executed.

So! How do I use Koadic through a port forward? Easy! Just make Koadic generate the correct URL right out of the gate. Set SRVHOST and SRVPORT to whatever address the target box needs to initiate connections to. It doesn't matter if that's not a local address on the host where Koadic is running. Koadic will just bind 0.0.0.0 and accept connections from anywhere.

-----

Stagers now have an AUTOFWD option that defaults to true. This is supposed to solve the problem posed above by checking out the Host header and using this to override SRVHOST and SRVPORT. If for some reason Host headers are not included in requests, then this will not work and you will need to follow the advice above. Setting AUTOFWD false will force stagers to not respect a differing Host header and Zombies will not attempt to stage.
""".strip()
    try:
        import textwrap
        msg2 = ""
        for paragraph in msg.split("\n\n"):
            msg2 += "\n".join(textwrap.wrap(paragraph))
            msg2 += "\n\n"
        msg = msg2.strip()
    except:
        pass
    shell.print_plain(msg)

def execute(shell, cmd):
    shell.print_plain("Sorry! This is just a stub-command to explain how to stage Koadic through a port forward. Windows Script Host is not smart enough for Koadic to do its own port forwards. You probably just want to stage a native RAT.");
