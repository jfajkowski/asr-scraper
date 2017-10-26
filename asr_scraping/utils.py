from datetime import datetime
from datetime import timedelta
from threading import Timer


def flatten(nested_list):
    return [item for sublist in nested_list for item in sublist]


class Scheduler:
    def __init__(self, run_time, function):
        self._run_time = run_time
        self._function = function
        self._schedule()

    @property
    def run_time(self):
        return self._run_time

    @run_time.setter
    def run_time(self, value):
        self._run_time = value
        self._schedule()

    def run(self):
        self._schedule()

    def _schedule(self):
        if self._timer:
            self._timer.cancel()

        self.time_scheduled = datetime.today()
        time_left = self._run_time - self.time_scheduled
        self._timer = Timer(interval=time_left.seconds(), function=self._run_and_reschedule())
        self._timer.run()

    def _run_and_reschedule(self):
        self._function()
        self._reschedule()

    def _reschedule(self):
        if self.run_time.year:
            self.run_time = self.run_time.replace(self.run_time.year + 1)
        elif self.run_time.month:
            self.run_time = self.run_time.replace((self.run_time.month + 1) % 12 + 1)
        else:
            self.run_time = self.run_time + timedelta(days=1)
