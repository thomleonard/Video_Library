from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'latest_magnet'
urlpatterns = [
    url(r'^$', views.library, name='library'),
    url(r'^tvshow_(?P<title_url>.+)_page/$',
    	views.tvshow_page, name='tvshow_page'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
