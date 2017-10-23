from fake_useragent import UserAgent
from lxml import html
import logging
import requests

class Scraper:
    USER_AGENTS = UserAgent()

    def __init__(self, config):
        self.logger = logging.getLogger(__name__)

        self._name = config['name']
        self._output_file = config['outputFile'] if 'outputFile' in config else ''
        self._subscrapers = [Scraper(subconfig) for subconfig in config['subscrapers']] if 'subscrapers' in config else []
        self._url = config['url']
        self._x_paths = config['xPaths'] if 'xPaths' in config else []

    def run(self):
        url = self._url
        response = self._get(url)
        contents = self._parse(response)
        if self._output_file:
            self._dump(contents)
        return contents

    def _get(self, url):
        headers = {'User-Agent': Scraper.USER_AGENTS.random}
        return requests.get(url, headers=headers)

    def _parse(self, response):
        tree = html.fromstring(response.content)
        contents = []
        for x_path in self._x_paths:
            content = tree.xpath(x_path)
            contents.append(content)
        return contents

    def _dump(self, contents):
        with open(self._output_file, encoding='UTF-8', mode='a') as f_out:
            for content in contents:
                f_out.write('\n'.join(content).rstrip() + '\n')