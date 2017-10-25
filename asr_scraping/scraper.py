import logging

import requests
from fake_useragent import UserAgent
from lxml import html
from lxml.html import HtmlElement

from utils import flatten


class Scraper:
    USER_AGENTS = UserAgent()

    def __init__(self, url, name='', output_file='', subscrapers=None, x_paths=None):
        self._logger = logging.getLogger(__name__)
        self._url = url
        self._name = name
        self._output_file = output_file
        self._subscrapers_definitions = subscrapers if subscrapers is not None else []
        self._x_paths = x_paths if x_paths is not None else []

    @property
    def subscrapers(self):
        return self._subscrapers_definitions

    def run(self, callback=None):
        response = self._get(self._url)
        contents = self._parse(response, self._x_paths)
        if self._output_file:
            self._dump(contents)
        for subscraper_definition in self._subscrapers_definitions:
            self._run_subscraper(response, callback, **subscraper_definition)

        if callback:
            callback(contents)

    @staticmethod
    def _get(url):
        headers = {'User-Agent': Scraper.USER_AGENTS.random}
        return requests.get(url, headers=headers)

    @staticmethod
    def _parse(response, x_paths):
        tree = html.fromstring(response.content)
        contents = []
        for x_path in x_paths:
            content = [c.xpath('string()') if isinstance(c, HtmlElement) else str(c) for c in tree.xpath(x_path)]
            contents.append(content)
        return contents

    def _dump(self, contents):
            with open(self._output_file, encoding='UTF-8', mode='a') as f_out:
                for content in contents:
                    f_out.write('\n'.join(content).rstrip() + '\n')

    def _run_subscraper(self, response, callback, subscraper_urls_x_paths, subscraper_config):
            subscraper_urls = self._parse(response, subscraper_urls_x_paths)
            for subscraper_url in flatten(subscraper_urls):
                if 'http' not in subscraper_url:
                    subscraper_url = self._url + subscraper_url
                subscraper = Scraper(subscraper_url, **subscraper_config)
                subscraper.run(callback)
