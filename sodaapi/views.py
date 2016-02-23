from django.http import HttpResponse
from sodaapi import api
import csv
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)
def get_all_crime(request):
    response = HttpResponse(content_type='text/csv')
    response['content-Disposition'] = 'attachment; filename="all_crime.csv"'

    # these could blow up, but that'll just return a 500, which is good for now
    writer = csv.writer(response)
    writer.writerows(api.get_crime_data())

    return response

@cache_page(60 * 15)
def get_grouped_crime(request):
    response = HttpResponse(content_type='text/csv')
    response['content-Disposition'] = 'attachment; filename="grouped_crime.csv"'

    # these could blow up, but that'll just return a 500, which is good for now
    writer = csv.writer(response)
    writer.writerows(api.get_grouped_crime_data())

    return response
