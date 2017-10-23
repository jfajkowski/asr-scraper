import unittest

from scraper import Scraper


class MyTestCase(unittest.TestCase):
    def test_python(self):
        mock_config = {
            'name': 'testScraper',
            'url': 'https://www.python.org/',
            'xPaths': ['//*[@id="touchnav-wrapper"]/header/div/h1/a/img/@alt']
        }
        mock_scraper = Scraper(mock_config)

        expected = [['python™']]
        actual = mock_scraper.run()

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
