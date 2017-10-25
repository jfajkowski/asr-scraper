import argparse
import json
import logging

from scheduled_scraper import ScheduledScraper
from periodic_scraper import PeriodicScraper
from scraper import Scraper


def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-a', '--async', dest='async', default=[], nargs='+')
    parser.add_argument('-p', '--periodic', dest='periodic', default=[], nargs='+')
    parser.add_argument('-s', '--scheduled', dest='scheduled', default=[], nargs='+')
    return parser.parse_args()

def run_async(scrapers):
    for path in scrapers:
        with open(path) as f_in:
            config = json.load(f_in)
            scraper = Scraper(**config)
            scraper.run()

def run_periodic(scrapers):
    for path in scrapers:
        with open(path) as f_in:
            config = json.load(f_in)
            scraper = PeriodicScraper(**config)
            scraper.run()

def run_scheduled(scrapers):
    for path in scrapers:
        with open(path) as f_in:
            config = json.load(f_in)
            scraper = ScheduledScraper(**config)
            scraper.run()

def main():
    args = parse_args()
    run_async(args.async)
    run_periodic(args.periodic)
    run_scheduled(args.scheduled)

    while True and (args.periodic or args.scheduled):
        if input('Type "EXIT" to exit.') == 'EXIT':
            break

if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(name)s: %(message)s', level=logging.INFO)
    main()