from bs4 import BeautifulSoup
from selenium import webdriver
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

ADDRESS = 'www.pw.edu.pl'


class Spider(CrawlSpider):
    name = ADDRESS
    allowed_domains = [ADDRESS]
    start_urls = ['http://' + ADDRESS]
    rules = [
        Rule(LinkExtractor(deny=('engpw', 'Uczelnia/Galeria', 'content/download')), callback='parse_item', follow=True)
    ]

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._driver = webdriver.Firefox()

    def parse_item(self, response):
        if 'html' in response.text:
            self._driver.get(response.url)
            soup = BeautifulSoup(self._driver.page_source)
            article = soup.find('div', attrs={'class': 'content-view-full'})
            if article:
                yield {
                    'url': response.url,
                    'text': article.get_text(separator='<SEP>')
                }