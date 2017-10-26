from scraper import Scraper
from threading import Timer


class PeriodicScraper(Scraper):
    def __init__(self, url, interval, ignore_failure=False, name='', output_file='', subscrapers=None, x_paths=None):
        super().__init__(url, name, output_file, subscrapers, x_paths)
        self._interval = interval
        self._ignore_failure = ignore_failure
        self._timer = None

    @property
    def timer(self):
        return self._timer

    def run(self, callback=None):
        self._timer = Timer(self._interval, function=lambda: super(self.__class__, self).run(callback))
        self._timer.start()
