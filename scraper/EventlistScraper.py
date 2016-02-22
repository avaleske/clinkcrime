from datetime import datetime
import re
import pytz
from bs4 import BeautifulSoup

def scrape(f):
    current_year = None
    soup = BeautifulSoup(f, 'html.parser')

    # get all the <tr> from the main event table
    # there's some weird escaping issues in the class, but it works out
    trs = soup.find('table', class_='\\"twSimpleTableTable\\"').find_all('tr')
    for tr in trs:
        if not tr.has_attr('class'):    # then it's the year row
            current_year = tr.td.div.string.split(' ')[1]
        elif tr['class'][0] == '\\"twSimpleTableEventRow0':   # it's the useful row

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
            # and convert it to a timezone aware datetime, and then a js timestamp
            dt = pytz.timezone(
                'America/Los_Angeles').localize(naive_datetime, is_dst=True)
            js_dt = (dt - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds() * 1000

            # get a cleaner location
            groups = re.match(r'^(CenturyLink Field|800 Occidental Ave)(?! Event Center)',
                    tr.contents[5].string or '')
            if groups is not None:
                location = "CenturyLink Field"
            else:
                location = tr.contents[5].string

            # get the rest
            title = tr.contents[4].string or ''
            trumba_id = int(tr.contents[0].input['value'].strip('\\"'))

            yield [trumba_id, js_dt, title, location]
        else: # it's not a row we care about
            continue
