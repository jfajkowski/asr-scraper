from scraper import Scraper
from utils import Scheduler


class ScheduledScraper(Scraper):
    def __init__(self, url, time, ignore_failure=False, name='', output_file='', subscrapers=None, x_paths=None):
        super().__init__(url, name, output_file, subscrapers, x_paths)
        self._time = time
        self._ignore_failure = ignore_failure
        self._scheduler = None

    @property
    def scheduler(self):
        return self._scheduler

    def run(self, callback=None):
        self._scheduler = Scheduler(self._time, function=lambda: super().run(callback))
        self._scheduler.run()
