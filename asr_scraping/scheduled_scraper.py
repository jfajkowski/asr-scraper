from scraper import Scraper
from utils import Scheduler


class PeriodicScraper(Scraper):
    def __init__(self, url, time, ignore_failure=False, name='', output_file='', subscrapers=None, x_paths=None):
        super().__init__(**locals())
        self._time = time
        self._ignore_failure = ignore_failure
        self._scheduler = None

    @property
    def scheduler(self):
        return self._scheduler

    def run(self, callback):
        self._scheduler = Scheduler(self._time, target=super().run(callback))
        self._scheduler.run()
