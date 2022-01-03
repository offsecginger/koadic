import threading

''' Updates clock and runs repeat jobs '''
class RepeatJobClock(object):

    def __init__(self, shell):
        self.shell = shell
        self.check_alive_timer = None
        self.check()

    def check(self):
        if self.check_alive_timer is not None:
            self.check_alive_timer.cancel()

        self.check_alive_timer = threading.Timer(1.0, self.check)
        self.check_alive_timer.daemon = True
        self.check_alive_timer.start()

        remove_jobs = []

        for rjob in self.shell.repeatjobs:
            rjobval = self.shell.repeatjobs[rjob]
            if rjobval[0] > 0:
                rjobval[0] = rjobval[0]- 1
                continue

            zombie = [o.value for o in rjobval[6].options if o.name == "ZOMBIE"][0]
            rjobval[7].dispatch(rjobval[2], rjobval[3], False, zombie)
            rjobval[0] = rjobval[4]

            if rjobval[1] == 0:
                continue
            if rjobval[1] > 2:
                rjobval[1] = rjobval[1] - 1
                continue

            remove_jobs.append(rjob)

        if remove_jobs:
            tmp = dict(self.shell.repeatjobs)
            for r in remove_jobs:
                del tmp[r]
            self.shell.repeatjobs = tmp
