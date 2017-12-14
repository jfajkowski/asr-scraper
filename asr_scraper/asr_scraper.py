import argparse
import json
import logging

from scraping import AutomaticScraper, BasicScraper, PeriodicScraper, ScheduledScraper


def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-a', '--automatic', dest='automatic', default=[], nargs='+')
    parser.add_argument('-b', '--basic', dest='basic', default=[], nargs='+')
    parser.add_argument('-p', '--periodic', dest='periodic', default=[], nargs='+')
    parser.add_argument('-s', '--scheduled', dest='scheduled', default=[], nargs='+')
    return parser.parse_args()


def run_scrapers(config_paths, scraper_type):
    for path in config_paths:
        with open(path) as f_in:
            config = json.load(f_in)
            scraper = scraper_type(**config)
            scraper.run()


def main():
    args = parse_args()
    run_scrapers(args.automatic, AutomaticScraper)
    run_scrapers(args.basic, BasicScraper)
    run_scrapers(args.periodic, PeriodicScraper)
    run_scrapers(args.scheduled, ScheduledScraper)

    while True and (args.periodic or args.scheduled):
        if input('Type "EXIT" to exit. ') == 'EXIT':
            break


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(name)s: %(message)s', level=logging.INFO)
    main()
