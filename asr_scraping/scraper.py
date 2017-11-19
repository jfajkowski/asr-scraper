import logging

import requests
from fake_useragent import UserAgent
from lxml import html
from lxml.html import HtmlElement

from utils import flatten


class Scraper:
    USER_AGENTS = UserAgent()

    def __init__(self, url, name='', output_file='', subscrapers=None,
                 contents_x_paths=None, next_page_x_path=None):
        self._logger = logging.getLogger(__name__)
        self._url = url
        self._name = name
        self._output_file = output_file
        self._subscrapers_definitions = subscrapers if subscrapers is not None else []
        self._contents_x_paths = contents_x_paths if contents_x_paths is not None else []
        self._next_page_x_path = next_page_x_path

    @property
    def subscrapers(self):
        return self._subscrapers_definitions

    def run(self, callback=None):
        while self._url:
            response = self._get(self._url)
            contents = self._batch_parse(response, self._contents_x_paths)
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

    @staticmethod
    def _get(url):
        headers = {'User-Agent': Scraper.USER_AGENTS.random}
        return requests.get(url, headers=headers)

    @staticmethod
    def _batch_parse(response, x_paths):
        tree = html.fromstring(response.content)
        contents = []
        for x_path in x_paths:
            content = [Scraper._to_string(c) for c in tree.xpath(x_path)]
            contents.append(content)
        return contents

    @staticmethod
    def _parse(response, x_path):
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

    def _run_subscraper(self, response, callback, subscraper_urls_x_paths, subscraper_config):
            subscraper_urls = self._batch_parse(response, subscraper_urls_x_paths)
            for subscraper_url in flatten(subscraper_urls):
                subscraper_url = Scraper._join(self._url, subscraper_url)
                subscraper = Scraper(subscraper_url, **subscraper_config)
                subscraper.run(callback)

    def _next_url(self, response):
        next_page_url = self._parse(response, self._next_page_x_path)
        next_page_url = Scraper._join(self._url, next_page_url)
        return next_page_url

    @staticmethod
    def _join(url_a, url_b):
        max_n = 0
        for n in range(1, 1 + min(len(url_a), len(url_b))):
            suffix = url_a[-n:]
            prefix = url_b[:n]
            if prefix == suffix:
                max_n = n
        return url_a + url_b[max_n:]
