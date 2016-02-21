from datetime import datetime
import pytz
from django.test import TestCase
from scraper.eventlist_scraper import EventlistScraper

# Create your tests here.
class EventlistScraperTests(TestCase):
    def test_scraper(self):
        with open('scraper/tests/test_event_list.html', 'r') as f:
            results = EventlistScraper.scrape(f)
            naive_datetime = datetime.strptime("2015 Sep 3 7pm", "%Y %b %d %I%p")
            aware_datetime = pytz.timezone(
                'America/Los_Angeles').localize(naive_datetime, is_dst=True)

            # check the total amount
            self.assertEqual(len(results),
                             49,
                             msg="Did not scrape expected number of events")

            # check the first item
            self.assertListEqual(
                results[0],
                [114569595,
                 aware_datetime,
                 "Seahawks vs Raiders (Preseason)",
                 "CenturyLink Field"],
                msg="First event data did not match"
            )
