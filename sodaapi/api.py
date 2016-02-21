from django.conf import settings
import itertools
from sodapy import Socrata



def get_crime_data():
    # call crime data api
    # this is a demo app, no point in cacheing for now

    client = Socrata(settings.SOURCE_DOMAIN, settings.SOCRATA_APP_TOKEN)

    limit = 20000
    offset = 0
    tries = 10

    data = []

    for i in xrange(tries):
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

        if len(response) == 1:  # just the headers
            break   # then there's nothing left to ask for

        # if it's not the first page, then trim off the header row
        # using itertools so we don't make a shallowcopy of the giant list
        response_iter = itertools.islice(response, 0 if i == 0 else 1, None)

        offset += len(response) - 1 # don't count the header
        data.extend(response_iter)
        print('loop ' + str(i))

    client.close()
    return data
