from scraper import Scraper
from threading import Timer


class PeriodicScraper(Scraper):
    def __init__(self, url, interval, ignore_failure=False, name='', output_file='', subscrapers=None, x_paths=None):
        super().__init__(**locals())
        self._interval = interval
        self._ignore_failure = ignore_failure
        self._timer = None

    @property
    def timer(self):
        return self._timer

    def run(self, callback=None):
        self._timer = Timer(self._interval, function=super().run(callback))
        self._timer.run()
