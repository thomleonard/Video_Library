from django.conf.urls import url

from . import views

app_name = 'latest_magnet'
urlpatterns = [
    url(r'^$', views.library, name='library'),
    url(r'^tvshow_(?P<title_url>.+)_page/$',
    	views.tvshow_page, name='tvshow_page'),
]