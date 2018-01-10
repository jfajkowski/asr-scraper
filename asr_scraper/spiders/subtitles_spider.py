import os
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

BASE_URL = 'https://www.opensubtitles.org'
DOWNLOAD_DIR = '/home/jfajkowski/Downloads/corpora/subtitles'
UBLOCK_FIREFOX_EXTENSION = '/home/jfajkowski/.mozilla/firefox/pcfvdgp3.default/extensions/uBlock0@raymondhill.net.xpi'

class Spider(scrapy.Spider):
    name = "www.opensubtitles.org"
    start_urls = [BASE_URL + '/pl/search/sublanguageid-pol/offset-240']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 1
        }
    }

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._profile = webdriver.FirefoxProfile()
        self._profile.set_preference('browser.download.folderList', 2)  # enable custom download dir
        self._profile.set_preference('browser.download.manager.showWhenStarting', False)
        self._profile.set_preference('browser.download.dir', DOWNLOAD_DIR)
        self._profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/zip')
        self._driver = None

    def start_driver(self):
        if self._driver:
            self._driver.close()

        self._driver = webdriver.Firefox(self._profile)
        self._driver.install_addon(UBLOCK_FIREFOX_EXTENSION)

    def parse(self, response):
        self.start_driver()
        self._driver.get(response.url)

        downloaded = 0
        while True:
            download_buttons = self._driver.find_elements(By.XPATH,
                                                          '//tr[@class="change odd expandable" or @class="change even expandable"]'
                                                          '/td[5]/a')
            try:
                for download_button in download_buttons[downloaded:]:
                    download_button.click()
                    self.logger.info('Downloading {}/{}'.format(downloaded + 1, len(download_buttons)))
                    downloaded += 1
                break
            except Exception:
                downloaded -= 1
                self.logger.warning('Captcha while downloading {}/{}!'.format(downloaded + 1, len(download_buttons)))

                self.start_driver()
                sleep(60)
                self._driver.get(response.url)

        next_page_href = response.xpath('//div[@class="pager-list"]/a[last()]/@href').extract_first()
        yield scrapy.Request(url=BASE_URL + next_page_href)
