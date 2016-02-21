from django.utils import timezone
from datetime import datetime
import requests
import pytz
from scraper import EventlistScraper

class ScraperRunner():
    def __init__(self, scraper=EventlistScraper()):
        self.scraper = scraper

    def scrape_events(self):
        trumba_url = 'http://www.trumba.com/s.aspx?hosted=1&template=table&calendar=centurylink-field-events-calendar&widget=main&date={0}&index=-1&srpc.cbid=trumba.spud.4&srpc.get=true'
        naive_earliest_date = datetime(2012, 1, 1)
        # and convert it to a timezone aware datetime
        earliest_date = pytz.timezone(
            'America/Los_Angeles').localize(naive_earliest_date, is_dst=True)
        current_date = timezone.now()
        all_events = []
        all_events.append([
            'trumba_id',
            'event_datetime',
            'title',
            'location'
        ])

        while current_date > earliest_date:
            date_as_string = current_date.strftime('%Y%m%d')
            r = requests.get(trumba_url.format(date_as_string))
            # thought I'd have to pull the html out of the returned object
            # but the parser handles it just fine for a demo app
            # there's also some url quoting issues happening, for the record
            events = self.scraper.scrape(r.text)
            all_events.extend(events)
            current_date = events[0][1] # events should be sorted by date already
        return all_events
