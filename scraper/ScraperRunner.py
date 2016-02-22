from datetime import datetime
from django.utils import timezone
import requests
import pytz
from scraper import EventlistScraper

class ScraperRunner():
    def __init__(self, scraper_func=EventlistScraper.scrape):
        self.scraper_func = scraper_func

    def scrape_events(self):
        trumba_url = 'http://www.trumba.com/s.aspx?hosted=1&template=table&calendar=centurylink-field-events-calendar&widget=main&date={0}&index=-1&srpc.cbid=trumba.spud.4&srpc.get=true'
        naive_earliest_date = datetime(2012, 1, 1)
        # and convert it to a timezone aware datetime
        earliest_date = pytz.timezone(
            'America/Los_Angeles').localize(naive_earliest_date, is_dst=True)
        current_date = timezone.now()
        yield ['trumba_id',
                'event_datetime',
                'title',
                'location']

        while current_date > earliest_date:
            date_as_string = current_date.strftime('%Y%m%d')
            r = requests.get(trumba_url.format(date_as_string))
            # thought I'd have to pull the html out of the returned js object
            # but the parser handles it just fine for a demo app
            for i, event in enumerate(self.scraper_func(r.text)):
                if i == 0:
                    # convert the first one back to datetime for comparison
                    current_date = pytz.utc.localize(datetime.utcfromtimestamp(event[1]/1000))
                yield event
