import logging
import re
from queue import Queue
from random import random
from time import sleep

import requests

from abc import ABC, abstractmethod
from fake_useragent import UserAgent
from lxml import html
from lxml.html import HtmlElement

from threading import Timer
from utils import flatten, Scheduler

USER_AGENTS = UserAgent()


class Scraper(ABC):
    SLEEP_MEAN = 5
    SLEEP_VARIANCE = 2.5
    URL_ROOT_PATTERN = re.compile('http[s]?://[^/]+/?')

    def __init__(self, url, name='', output_file=''):
        self._logger = logging.getLogger(__name__)
        self._url = url
        self._name = name
        self._output_file = output_file

    @abstractmethod
    def run(self, callback=None):
        pass

    def _get(self, url):
        self._sleep()
        self._logger.info('Request to: {}'.format(url))
        headers = {'User-Agent': USER_AGENTS.random}
        return requests.get(url, headers=headers)

    def _sleep(self):
        sleep(Scraper.SLEEP_MEAN + (random() - 0.5) * 2 * Scraper.SLEEP_VARIANCE)

    def _parse_batch(self, response, x_paths):
        tree = html.fromstring(response.content)
        contents = []
        for x_path in x_paths:
            content = [Scraper._to_string(c) for c in tree.xpath(x_path)]
            contents.append(content)
        self._logger.info('Got {} elements.'.format(len(contents)))
        return contents

    @staticmethod
    def _parse_list(response, x_path):
        tree = html.fromstring(response.content)
        content = [Scraper._to_string(c) for c in tree.xpath(x_path)]
        return content

    @staticmethod
    def _parse_single(response, x_path):
        tree = html.fromstring(response.content)
        content = [Scraper._to_string(c) for c in tree.xpath(x_path)]
        if len(content) > 1:
            raise ValueError('XPath {} is ambiguous.'.format(x_path))
        return content[0] if len(content) == 1 else None

    @staticmethod
    def _to_string(content):

        return content.xpath('string()') if isinstance(content, HtmlElement) else str(content)

    def _dump(self, contents):
        with open(self._output_file, encoding='UTF-8', mode='a') as f_out:
            for content in contents:
                f_out.write('\n'.join(content).rstrip() + '\n')

    @staticmethod
    def _join(url_a, url_b):
        if Scraper.URL_ROOT_PATTERN.search(url_b):
            return url_b
        else:
            return Scraper.URL_ROOT_PATTERN.search(url_a)[0] + url_b[1:]

    @staticmethod
    def _common_domain(url_a, url_b):
        url_a_domain = Scraper.URL_ROOT_PATTERN.search(url_a)
        if not url_a_domain:
            return None

        url_b_domain = Scraper.URL_ROOT_PATTERN.search(url_b)
        if not url_b_domain:
            return None

        if url_a_domain[0] == url_b_domain[0]:
            return url_a_domain[0]
        else:
            return None


class BasicScraper(Scraper):
    def __init__(self, url, name='', output_file='', subscrapers=None,
                 contents_x_paths=None, next_page_x_path=None):
        super().__init__(url, name, output_file)
        self._subscrapers_definitions = subscrapers if subscrapers is not None else []
        self._contents_x_paths = contents_x_paths if contents_x_paths is not None else []
        self._next_page_x_path = next_page_x_path

    def run(self, callback=None):
        while self._url:
            response = self._get(self._url)
            contents = self._parse_batch(response, self._contents_x_paths)
            if self._output_file:
                self._dump(contents)
            for subscraper_definition in self._subscrapers_definitions:
                self._run_subscraper(response, callback, **subscraper_definition)

            if self._next_page_x_path:
                self._url = self._next_url(response)
            else:
                self._url = None

            if callback:
                callback(contents)

    def _run_subscraper(self, response, callback, subscraper_urls_x_paths, subscraper_config):
        subscraper_urls = self._parse_batch(response, subscraper_urls_x_paths)
        for subscraper_url in flatten(subscraper_urls):
            subscraper_url = Scraper._join(self._url, subscraper_url)
            subscraper = Scraper(subscraper_url, **subscraper_config)
            subscraper.run(callback)

    def _next_url(self, response):
        next_page_url = self._parse_single(response, self._next_page_x_path)
        next_page_url = Scraper._join(self._url, next_page_url)
        return next_page_url


class PeriodicScraper(BasicScraper):
    def __init__(self, url, interval, ignore_failure=False, name='', output_file='', subscrapers=None,
                 contents_x_paths=None, next_page_x_path=None):
        super().__init__(url, name, output_file, subscrapers,
                         contents_x_paths, next_page_x_path)
        self._interval = interval
        self._ignore_failure = ignore_failure
        self._timer = None

    @property
    def timer(self):
        return self._timer

    def run(self, callback=None):
        self._timer = Timer(self._interval, function=lambda: super(self.__class__, self).run(callback))
        self._timer.start()


class ScheduledScraper(BasicScraper):
    def __init__(self, url, time, ignore_failure=False, name='', output_file='', subscrapers=None,
                 contents_x_paths=None, next_page_x_path=None):
        super().__init__(url, name, output_file, subscrapers,
                         contents_x_paths, next_page_x_path)
        self._time = time
        self._ignore_failure = ignore_failure
        self._scheduler = None

    @property
    def scheduler(self):
        return self._scheduler

    def run(self, callback=None):
        self._scheduler = Scheduler(self._time, function=lambda: super().run(callback))
        self._scheduler.run()


class AutomaticScraper(Scraper):
    URLS_XPATH = './/*/@href'
    TEXT_XPATH = './/*[text()]'
    ACCEPTED_URL_ANTIPATTERN = re.compile(r'^https?://.+/.+\..+$')
    ACCEPTED_URL_SUFFIXES = ['html', 'htm']

    def __init__(self, url, ignore_failure=False, name='', output_file='', contents_x_paths=None):
        super().__init__(url, name, output_file)
        self._contents_x_paths = contents_x_paths if contents_x_paths is not None else [AutomaticScraper.TEXT_XPATH]
        self._ignore_failure = ignore_failure
        self._root_url = AutomaticScraper.URL_ROOT_PATTERN.search(self._url)[0]
        self._urls = Queue()
        self._visited_urls = set()

    def run(self, callback=None):
        while self._url:
            response = self._get(self._url)
            self._visited_urls.add(self._url)
            contents = self._parse_batch(response, self._contents_x_paths)
            for url in self._parse_list(response, AutomaticScraper.URLS_XPATH):
                url = self._join(self._root_url, url)
                if self._common_domain(self._root_url, url) and url not in self._visited_urls and self._is_accepted(url):
                    self._urls.put(url)

            if self._output_file:
                self._dump(contents)

            if self._urls.empty():
                self._url = None
            else:
                self._url = self._urls.get()

            if callback:
                callback(contents)

    @staticmethod
    def _is_accepted(url):
        if AutomaticScraper.ACCEPTED_URL_ANTIPATTERN.match(url):
            for suffix in AutomaticScraper.ACCEPTED_URL_SUFFIXES:
                if url.endswith(suffix):
                    break
            else:
                return False
        return True

