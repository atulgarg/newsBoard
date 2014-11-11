from django.conf.urls import patterns, include, url

from django.contrib import admin

from userHomePage.views import home, news
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'newsBoard.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)), url(r'^$', home),
    url(r'^news/', news),
)
