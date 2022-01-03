import threading
import time
import os

''' Timer to check and write restore file '''
class RestoreClock(object):

    def __init__(self, shell):
        self.shell = shell
        self.check_alive_timer = None
        self.restore_interval = 60 # seconds between each restore check
        self.restore_time = time.time()+self.restore_interval
        self.restore_dir = "restores/"
        self.restore_fname = self.restore_dir+time.strftime("%Y%m%d-%H%M%S")+".json"
        self.check_restores()
        self.check()

    def check_restores(self):
        if not os.path.exists(self.restore_dir):
            try:
                os.mkdir(self.restore_dir)
            except OSError:
                self.shell.print_error("Could not create restore directory!")

    def check(self):
        if self.check_alive_timer is not None:
            self.check_alive_timer.cancel()

        self.check_alive_timer = threading.Timer(1.0, self.check)
        self.check_alive_timer.daemon = True
        self.check_alive_timer.start()

        now = time.time()

        if now < self.restore_time:
            return

        self.restore_time += self.restore_interval

        if not self.shell.update_restore:
            return

        restore_map = {}
        restore_map['creds'] = self.convert_to_parsable(self.shell.creds)
        restore_map['creds_keys'] = self.convert_to_parsable(self.shell.creds_keys)
        restore_map['domain_info'] = self.convert_to_parsable(self.shell.domain_info)
        restore_map['jobs'] = []
        for jkey, j in self.shell.jobs.items():
            new_j = {}
            new_j['results'] = j.results
            new_j['id'] = j.id
            new_j['session_id'] = -1
            new_j['completed'] = j.completed
            new_j['ip'] = j.ip
            new_j['name'] = j.name
            restore_map['jobs'].append(new_j)

        restore_map['sessions'] = []
        for s in [vars(session) for skey, session in self.shell.sessions.items()]:
            new_s = dict(s)
            try:
                new_s.pop('stager')
                new_s.pop('shell')
            except:
                pass
            new_s['status'] = 0
            restore_map['sessions'].append(new_s)
        restore = open(self.restore_fname+".tmp", 'w')
        import json
        restore.write(json.dumps(restore_map)+"\n")
        restore.close()
        os.rename(self.restore_fname+".tmp", self.restore_fname)
        self.shell.update_restore = False

    def convert_to_parsable(self, obj):
        if isinstance(obj, dict):
            new_obj = {}
            for key in obj:
                if isinstance(key, tuple):
                    new_obj['/'.join(key)] = obj[key]
                elif isinstance(key, str):
                    new_obj[key] = obj[key]

        elif isinstance(obj, list):
            new_obj = []
            for val in obj:
                if isinstance(val, tuple):
                    new_obj.append('/'.join(val))
                elif isinstance(val, str):
                    new_obj.append(val)
        else:
            new_obj = []

        return new_obj
