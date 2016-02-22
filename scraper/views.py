from django.http import HttpResponse
from django.views.defaults import server_error
import csv
from scraper import ScraperRunner
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)
def get_all_events(request):
    response = HttpResponse(content_type='text/csv')
    response['content-Disposition'] = 'attachment; filename="all_events.csv"'
    writer = csv.writer(response)
    server_error(request)

    # these could blow up, but that'll just return a 500, which is good for now
    sr = ScraperRunner()
    writer.writerows(sr.scrape_events())

    return response
