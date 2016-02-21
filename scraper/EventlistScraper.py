from datetime import datetime
import pytz
import re
from bs4 import BeautifulSoup

class EventlistScraper():
    def __init__(self):
        # time_regex = re.compile('^([0-9]{1,2})(:[0-9]{2})?([ap]m)')
        pass

    @classmethod
    def scrape(cls, f):
        results = []
        current_year = None
        soup = BeautifulSoup(f, 'html.parser')

        # get all the <tr> from the main event table
        # no, I don't know why the class is escaped that way either...
        trs = soup.find('table', class_='\\"twSimpleTableTable\\"').find_all('tr')
        for tr in trs:
            if not tr.has_attr('class'):    # then it's the year row
                current_year = tr.td.div.string.split(' ')[1]
            elif tr['class'][0] == '\\"twSimpleTableEventRow0':   # it's the useful row
                trumba_id = int(tr.contents[0].input['value'].strip('\\"'))
                # get a datetime based on what we know
                t = re.match('^([0-9]{1,2})(:[0-9]{2})?([ap]m)', tr.contents[3].string or '')
                naive_datetime = datetime.strptime(
                    "{0} {1} {2}{3}{4}".format(
                        current_year,
                        re.match(r'^([A-z]{3} [0-9]{1,2})', tr.contents[2].string).group(0),
                        # add the hour if it exists, otherwise midnight
                        t.group(1) if t is not None else '12',
                        # add minutes if necessary
                        t.group(2) if t is not None and t.group(2) else ':00',
                        # then add the am/pm
                        t.group(3) if t is not None else 'am'),
                    "%Y %b %d %I:%M%p")
                # and convert it to a timezone aware datetime
                dt = pytz.timezone(
                    'America/Los_Angeles').localize(naive_datetime, is_dst=True)
                title = tr.contents[4].string or ''
                location = tr.contents[5].string or ''
                result = [trumba_id, dt, title, location]
                results.append(result)
            else:
                continue

        return results
