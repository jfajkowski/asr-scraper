import unittest

from scraping import ManualScraper


class ScraperTest(unittest.TestCase):
    def test_python_scraper(self):
        mock_config = {
            'name': 'testScraper',
            'url': 'https://www.python.org/',
            'contents_x_paths': ['//*[@id="touchnav-wrapper"]/header/div/h1/a/img/@alt']
        }
        mock_scraper = ManualScraper(**mock_config)

        expected = [['python™']]
        mock_scraper.run(lambda actual: self.assertEqual(expected, actual))

    def test_python_scraper_with_subscrapers(self):
        mock_config = {
            'name': 'testScraper',
            'url': 'https://www.python.org/',
            'contents_x_paths': ['//*[@id="touchnav-wrapper"]/header/div/h1/a/img/@alt'],
            'subscrapers': [{
                'subscraper_urls_x_paths': ['//*[@id="touchnav-wrapper"]/header/div/h1/a/@href'],
                'subscraper_config': {
                    'name': 'testSubscraper',
                    'contents_x_paths': ['//*[@id="touchnav-wrapper"]/header/div/h1/a/img/@alt']
                }}]
        }
        mock_scraper = ManualScraper(**mock_config)

        expected = [['python™']]
        mock_scraper.run(lambda actual: self.assertEqual(expected, actual))


if __name__ == '__main__':
    unittest.main()
