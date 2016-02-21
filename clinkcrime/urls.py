from django.conf.urls import include, url
from django.contrib import admin
# probs import the urls file in the future
import main.views
import sodaapi.views

urlpatterns = [
    # Examples:
    # url(r'^$', 'clinkcrime.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', main.views.index, name='index'),
    url(r'^api/all_crime$', sodaapi.views.get_all_crime, name='all_crime')
]
