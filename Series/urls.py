from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'Series'

urlpatterns = [

    # TV Shows library
    url(r'^$', views.library, name='library'),

    # TV Shows search page
    url(r'^search/$', views.search, name='search'),

    # empty the TV Shows library
    url(r'^empty_library/$', views.empty_library, name='empty_library'),

    # show the upcoming TV Show episodes from the library
    url(r'^upcoming/$', views.upcoming, name='upcoming'),

    # TV Show page
    url(r'^tvshow_(?P<tvshow_pk>\d+)/$',
    	views.tvshow_page, name='tvshow_page'),

    # episode seen view
    url(r'^seen_(?P<episode_pk>\d+)/$',
    	views.episode_seen, name='seen'),

    # episode seen view
    url(r'^magnet_(?P<episode_pk>\d+)/$',
        views.episode_magnet, name='magnet'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
