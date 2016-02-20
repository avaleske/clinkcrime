from django.conf.urls import include, url
from django.contrib import admin
# probs import the urls file in the future
import main.views

urlpatterns = [
    # Examples:
    # url(r'^$', 'clinkcrime.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', main.views.index, name='index')
]
