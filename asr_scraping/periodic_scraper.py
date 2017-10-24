from scraper import Scraper
from threading import Timer

class PeriodicScraper(Scraper):
    def __init__(self, config):
        super().__init__(config)
        self._interval = config['interval'] if 'interval' in config else 0
        self._ignore_failure = config['ignoreFailure'] if 'ignoreFailure' in config else False
        self._timer = None

    @property
    def timer(self):
        return self._timer

    def run(self, callback):
        self._timer = Timer(self._interval, function=super().run(callback))
        self._timer.run()
