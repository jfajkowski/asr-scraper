from datetime import datetime
from threading import Timer


def flatten(nested_list):
    return [item for sublist in nested_list for item in sublist]


class Scheduler:
    def __init__(self, run_time, interval, target):
        self._run_time = run_time
        self._interval = interval
        self._target = target
        self._schedule()

    @property
    def run_time(self):
        return self._run_time

    @run_time.setter
    def run_time(self, value):
        self._run_time = value
        self._schedule()

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value):
        self._run_time = value
        self._schedule()

    def _schedule(self):
        if self._timer:
            self._timer.cancel()

        self.time_scheduled = datetime.today()
        time_left = self._run_time - self.time_scheduled
        self._timer = Timer(interval=time_left.seconds(), function=self._run_and_reschedule())
        self._timer.run()

    def _run_and_reschedule(self):
        self._target()
        self._run_time = self._run_time + self._interval
        self._schedule()
