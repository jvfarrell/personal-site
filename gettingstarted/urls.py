from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import hello.views
import lol.views

# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'^db', hello.views.db, name='db'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', hello.views.home),
    url(r'^resume/$', hello.views.resume),
    url(r'^home/$', hello.views.home),
    url(r'^quote/$',hello.views.quote),
    url(r'^nfl/$', hello.views.nfl_analytics),
    url(r'^summoner/$', lol.views.summoner_landing),
    url(r'^summoner/(.*)/$', lol.views.summoner),
    url(r'^error/$', lol.views.error),
    url(r'^videos/$', hello.views.videos_page),
    url(r'^riot.txt$', hello.views.riot)
	url(r'^pat/$', hello.views.pat)
	url(r'^groomsmen/$', hello.views.groomsmen)

]
