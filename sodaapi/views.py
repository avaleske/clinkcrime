from django.http import HttpResponse
from sodaapi import api
from django.views.defaults import server_error
import csv
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)
def get_all_crime(request):
    response = HttpResponse(content_type='text/csv')
    response['content-Disposition'] = 'attachment; filename="all_crime.csv"'

    writer = csv.writer(response)
    try:
        writer.writerows(api.get_crime_data())
    except:
        server_error(request)  # this would've happened anyway, but we'll call it explicitly

    return response
