import core.rest_server
import time
import sys
import os

DESCRIPTION = "turn off/on the rest api"

def autocomplete(shell, line, text, state):
    return None

def help(shell):
    shell.print_plain("")
    shell.print_plain("Turning on the REST Server:")
    shell.print_plain("api on (--user USERNAME --pass PASSWORD --port PORT)")
    shell.print_plain("Username and password defaults to 'koadic'. Port defaults to 9990.")
    shell.print_plain("")
    shell.print_plain("Turning off the REST Server:")
    shell.print_plain("api off")
    shell.print_plain("")

def execute(shell, cmd):

    splitted = cmd.split()

    if len(splitted) > 1:
        username = "koadic"
        password = "koadic"
        port = "9990"
        remote = False
        secure = []
        if "--user" in splitted:
            username = splitted[splitted.index("--user")+1]
        if "--pass" in splitted:
            password = splitted[splitted.index("--pass")+1]
        if "--port" in splitted:
            port = splitted[splitted.index("--port")+1]
        if "--remote" in splitted:
            remote = True
            if "--cert" in splitted and "--key" in splitted:
                secure = [splitted[splitted.index("--cert")+1], splitted[splitted.index("--key")+1]]

        sw = splitted[1].lower()
        if sw == "on":
            if not shell.rest_thread:
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    s.bind(('127.0.0.1', int(port)))
                except OSError as e:
                    if e.errno == 98:
                        shell.print_error("Port %s is already bound!" % (port))
                    elif e.errno == 13:
                        shell.print_error("Port %s bind permission denied!" % (port))
                    s.close()
                    return
                s.close()

                rest_server = core.rest_server.RestServer(shell, port, username, password, remote, secure)
                def thread_rest_server():
                    try:
                        rest_server.run()
                    except SystemExit:
                        pass


                shell.rest_thread = core.rest_server.KThread(target=thread_rest_server)
                shell.rest_thread.daemon = True
                stdout = sys.stdout
                f = open(os.devnull, 'w')
                sys.stdout = f
                shell.rest_thread.start()
                time.sleep(2)
                sys.stdout = stdout
                # ok, now THIS is the most embarassing thing i've ever done.
                # i don't know how to pass exceptions from the thread to the caller.
                # so here we are.
                if "started" in shell.rest_thread.localtrace(0,0,0).__str__():
                    shell.print_good("Rest server running on port %s" % port)
                    shell.print_status("Username: %s" % username)
                    shell.print_status("Password: %s" % password)
                    shell.print_status("API Token: %s" % rest_server.token)
                else:
                    shell.rest_thread.kill()
                    shell.rest_thread = ""
                    shell.print_error("Could not start rest server.")

            else:
                shell.print_error("Rest server already running")
        elif sw == "off":
            if shell.rest_thread:
                shell.rest_thread.kill()
                shell.rest_thread = ""
                shell.print_good("Rest server shutdown")
            else:
                shell.print_error("Rest server not running")

    else:
        help(shell)
