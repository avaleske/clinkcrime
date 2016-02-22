import time
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


def get_grouped_crime_data():
    # call crime data api
    client = Socrata(settings.SOURCE_DOMAIN, settings.SOCRATA_APP_TOKEN)

    limit = 20000
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
            where='event_clearance_date is not null and \
                    within_circle(incident_location, {0}, {1}, {2})'.format(
                        settings.CLINK_LAT, settings.CLINK_LON, settings.RADIUS),
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
    return int(time.mktime(dt.timetuple())) * 1000
