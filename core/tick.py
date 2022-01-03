import core.extant
import core.repeatjobclock
import core.restoreclock

''' Kick off clocks '''
class Tick(object):

    def __init__(self, shell):
        self.start_timers(shell)

    def start_timers(self, shell):
        self.extant = core.extant.Extant(shell)
        self.repeatjobclock = core.repeatjobclock.RepeatJobClock(shell)
        self.restoreclock = core.restoreclock.RestoreClock(shell)
