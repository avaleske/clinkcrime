from django.http import HttpResponse
from django.views.defaults import server_error
import csv
from scraper import ScraperRunner

def get_all_events(request):
    response = HttpResponse(content_type='text/csv')
    response['content-Disposition'] = 'attachment; filename="all_crime.csv"'

    writer = csv.writer(response)
    try:
        sr = ScraperRunner()
        writer.writerows(sr.scrape_events())
    except:
        server_error(request)  # this would've happened anyway, but we'll call it explicitly

    return response
