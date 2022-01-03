import os
import sys
import traceback
import threading

import core.loader
import core.colors
import core.job
import core.tick

''' Cmd is just a bad wrapper around readline with buggy input '''
class Shell(object):

    def __init__(self, banner, version):
        self.banner = banner
        self.version = version
        self.actions = core.loader.load_plugins("core/commands")
        self.plugins = core.loader.load_plugins("modules", True, self)
        self.servers = {}
        self.sessions = {}
        self.stagers = {}
        self.jobs = {}
        self.repeatjobs = {}
        self.state = "stager/js/mshta"
        self.colors = core.colors.Colors()
        self.tick = core.tick.Tick(self)
        self.verbose = False
        self.creds = {}
        self.creds_keys = []
        self.domain_info = {}
        self.sounds = {}
        self.rest_thread = ""
        self.continuesession = ""
        self.update_restore = False
        self.spool = False
        self.spool_lock = threading.Lock()

    def run(self, autorun = [], restore_map = {}):
        self.main_thread_id = threading.current_thread().ident

        self.print_banner()

        if restore_map:
            self.restore(restore_map)

        while True:
            try:
                self.prompt = self.colors.get_prompt(self.state, True)
                self.clean_prompt = self.colors.get_prompt(self.state, False)

                cmd = ""
                while len(autorun) > 0:
                    cmd = autorun.pop(0).split("#")[0].strip()
                    if len(cmd) > 0:
                        break

                if len(cmd) == 0:
                    cmd = self.get_command(self.prompt, self.autocomplete, self.base_filenames)
                else:
                    print(self.clean_prompt + cmd)

                if self.spool:
                        self.spool_log(self.clean_prompt, cmd)


                self.run_command(cmd)

            except KeyboardInterrupt:
                self.confirm_exit()
            except EOFError:
                self.run_command("exit")
            except Exception:
                self.print_plain(traceback.format_exc())

    def confirm_prompt(self, msg):
        sys.stdout.write(os.linesep)
        try:
            res = "n"
            res = self.get_command("%s " % (msg))
        except:
            sys.stdout.write(os.linesep)

        return res.strip().lower()

    def confirm_exit(self):
        res = self.confirm_prompt("Exit? y/N:")

        if res.strip().lower() == "y":
            self.run_command("exit")

    def run_command(self, cmd):
        if not cmd:
            return
        action = cmd.split()[0].lower()
        remap = {
            "?": "help",
            "exploit": "run",
            "execute": "run",
            "ruin": "run",
            "doit": "run",
            "options": "info",
            "quit": "exit",
            "sessions": "zombies",
        }
        if action in self.actions:
            self.actions[action].execute(self, cmd)
        elif action in remap:
            cmd.replace(action, remap[action])
            self.actions[remap[action]].execute(self, cmd)
        else:
            try:
                self.print_error("Unrecognized command, you need 'help'.")

                #
                # bash lol:
                #os.system(cmd)
            except:
                pass

    def get_command(self, prompt, auto_complete_fn=None, basefile_fn=None):
        try:
            if auto_complete_fn != None:
                import readline
                readline.set_completer_delims(' \t\n;/')
                readline.parse_and_bind("tab: complete")
                readline.set_completer(auto_complete_fn)
                # readline.set_completion_display_matches_hook(basefile_fn)
        except:
            pass

        # python3 changes raw input name
        if sys.version_info[0] == 3:
            raw_input = input
        else:
            raw_input = __builtins__['raw_input']

        cmd = raw_input("%s" % prompt)
        return cmd.strip()

    def autocomplete(self, text, state):
        import readline
        line = readline.get_line_buffer()
        splitted = line.lstrip().split(" ")

        # if there is a space, delegate to the commands autocompleter
        if len(splitted) > 1:
            if splitted[0] in self.actions:
                if splitted[0] == "set" and splitted[1] == "MODULE" and len(splitted) < 4:
                    return self.actions["use"].autocomplete(self, line, text, state)
                return self.actions[splitted[0]].autocomplete(self, line, text, state)
            else:
                return None

        remap = {
            "?": "help",
            "exploit": "run",
            "execute": "run",
            "options": "info",
            "quit": "exit",
            "sessions": "zombies",
        }

        # no space, autocomplete will be the basic commands:
        options = [x + " " for x in self.actions if x.startswith(text)]
        options.extend([x + " " for x in remap if x.startswith(text)])
        try:
            return options[state]
        except:
            return None

    def base_filenames(self, substitution, matches, longest_match_length):
        pass
    #     print()
    #     print("substitution", substitution)
    #     print("matches", matches)
    #     print("length", longest_match_length)
    #     matches[:] = ["banana"]
    #     return "banana"
    #     # sys.stdout.flush()

    def print_banner(self):
        os.system("clear")

        implant_len = len([a for a in self.plugins
                           if a.startswith("implant")])
        stager_len = len([a for a in self.plugins
                          if a.startswith("stager")])
        print(self.banner % (self.version, stager_len, implant_len))

    def spool_log(self, prompt, text):
        with self.spool_lock:
            with open(self.spool, 'a+') as f:
                f.write(prompt + text + os.linesep)
                f.flush()

    def print_plain(self, text, redraw = False):
        sys.stdout.write("\033[1K\r" + text + os.linesep)
        if self.spool:
            self.spool_log("\033[1K\r", text)

        sys.stdout.flush()

        if redraw or threading.current_thread().ident != self.main_thread_id:
            import readline
            #sys.stdout.write("\033[s")
            sys.stdout.write(self.clean_prompt + readline.get_line_buffer())
            #sys.stdout.write("\033[u\033[B")
            sys.stdout.flush()

    def print_text(self, sig, text, redraw = False):
        self.print_plain(sig + " " + text, redraw)

    def print_good(self, text, redraw = False):
        self.print_text(self.colors.good("[+]"), text, redraw)

    def print_warning(self, text, redraw = False):
        self.print_text(self.colors.warning("[!]"), text, redraw)

    def print_error(self, text, redraw = False):
        self.print_text(self.colors.error("[-]"), text, redraw)

    def print_status(self, text, redraw = False):
        self.print_text(self.colors.status("[*]"), text, redraw)

    def print_verbose(self, text, redraw = False):
        if self.verbose:
            self.print_text(self.colors.colorize("[v]", [self.colors.BOLD]), text, redraw)

    def print_help(self, text, redraw = False):
        self.print_text(self.colors.colorize("[?]", [self.colors.BOLD]), text, redraw)

    def print_command(self, text, redraw = False):
        self.print_text(self.colors.colorize("[>]", [self.colors.BOLD]), text, redraw)

    def print_hash(self, text, redraw = False):
        self.print_text(self.colors.colorize("[#]", [self.colors.BOLD]), text, redraw)

    def play_sound(self, enum):
        if enum in self.sounds:
            sound = self.sounds[enum]
            if type(sound) is list:
                import random
                sound = random.choice(sound)

            threading.Thread(target=self.play_audio_file, args=[sound]).start()

    def play_audio_file(self, audio_file):
        from playsound import playsound
        try:
            playsound(audio_file)
        except:
            if not os.path.isfile(audio_file):
                self.print_error('Could not play sound file %s. Check if path to file is correct.' % audio_file)

    def restore(self, restore_map):
        for key in restore_map['creds']:
            self.creds[tuple(key.split('/'))] = restore_map['creds'][key]

        for val in restore_map['creds_keys']:
            self.creds_keys.append(tuple(val.split('/')))

        for key in restore_map['domain_info']:
            self.domain_info[tuple(key.split('/'))] = restore_map['domain_info'][key]

        class RestoreJob():
            def __init__(self, shell):
                self.shell = shell

            def display(self):
                self.shell.print_plain(self.results)

            def status_string(self):
                if self.completed == 4:
                    return "Complete"
                else:
                    return "Failed"

        for job in restore_map['jobs']:
            rs_job = RestoreJob(self)
            for k,v in job.items():
                setattr(rs_job, k, v)
            self.jobs[rs_job.key] = rs_job

        class RestoreStager():
            def __init__(self, payload):
                self.payload = payload

        class RestorePayload():
            def __init__(self):
                self.id = '-1'

        class RestoreSession():
            def __init__(self, shell):
                self.shell = shell

            def set_reconnect(self):
                pass

            def kill(self):
                self.killed = True
                self.shell.print_good("Zombie %d: Killed!" % self.id)

        rs_stager = RestoreStager(RestorePayload())
        for session in restore_map['sessions']:
            rs_session = RestoreSession(self)
            for k,v in session.items():
                setattr(rs_session, k, v)
            rs_session.stager = rs_stager

            self.sessions[rs_session.key] = rs_session
