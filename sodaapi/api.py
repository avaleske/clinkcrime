from datetime import datetime
from itertools import imap, islice
from sodapy import Socrata
from django.conf import settings
import pytz


def get_crime_data():
    # call crime data api
    client = Socrata(settings.SOURCE_DOMAIN, settings.SOCRATA_APP_TOKEN)

    limit = 20000
    offset = 0
    tries = 10

    # return the headers
    yield ['cad_cdw_id', 'event_clearance_date', 'event_clearance_group']

    for _ in xrange(tries):
        # sodapy throws an exception if we get a bad response
        # no need to handle it here, we'll catch it on the outside
        response = client.get(
            settings.DATASET_ID,
            content_type="csv",
            select='cad_cdw_id, event_clearance_group, event_clearance_date',
            where='event_clearance_date is not null and \
                    within_circle(incident_location, {0}, {1}, {2})'.format(
                        settings.CLINK_LAT, settings.CLINK_LON, settings.RADIUS),
            order='event_clearance_date DESC',
            limit=limit,
            offset=offset
        )
        offset += len(response) - 1 # don't count the header
        if len(response) == 1:  # if it's just the header
            break   # then there's nothing left to ask for

        # trim off the header row
        # using itertools so we don't make a shallow copy of the giant list
        response_iter = islice(response, 1, None)
        for row in imap(_convert_row, response_iter):
            yield row
    client.close()


def get_grouped_crime_data(start, end):
    seattle_time = pytz.timezone('America/Los_Angeles')

    start_date = pytz.utc.localize(datetime.utcfromtimestamp(int(start)/1000))
    local_start_date = start_date.astimezone(seattle_time).replace(tzinfo=None)

    end_date = pytz.utc.localize(datetime.utcfromtimestamp(int(end)/1000))
    local_end_date = end_date.astimezone(seattle_time).replace(tzinfo=None)

    # call crime data api
    client = Socrata(settings.SOURCE_DOMAIN, settings.SOCRATA_APP_TOKEN)

    limit = 2000
    offset = 0
    tries = 10

    # return the headers
    yield ['count', 'date', 'event_clearance_group']

    for _ in xrange(tries):
        # sodapy throws an exception if we get a bad response
        # no need to handle it here, we'll catch it on the outside
        response = client.get(
            settings.DATASET_ID,
            content_type="csv",
            select='date_trunc_ymd(event_clearance_date) as date, event_clearance_group, count(*)',
            where='event_clearance_date is not null \
                    and event_clearance_date >= \'{0}\' \
                    and event_clearance_date <= \'{1}\' \
                    and within_circle(incident_location, {2}, {3}, {4})'.format(
                        local_start_date.isoformat().split('+')[0],
                        local_end_date.isoformat().split('+')[0],
                        settings.CLINK_LAT,
                        settings.CLINK_LON,
                        settings.RADIUS),
            group='date, event_clearance_group',
            order='date DESC, count DESC',
            limit=limit,
            offset=offset
        )
        offset += len(response) - 1 # don't count the header
        if len(response) == 1:  # if it's just the header
            break   # then there's nothing left to ask for

        # trim off the header row
        # using itertools so we don't make a shallow copy of the giant list
        response_iter = islice(response, 1, None)
        for row in imap(_convert_grouped_row, response_iter):
            yield row
    client.close()

# utils

def _convert_row(row):
    row[1] = _convert_date_to_js(row[1])
    return row

def _convert_grouped_row(row):
    row[1] = _convert_date_to_js(row[1])
    return row

def _convert_date_to_js(date_string):
    dt = pytz.timezone('America/Los_Angeles').localize(
        datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.000'), is_dst=True)
    js_dt = (dt - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds() * 1000
    return js_dt
