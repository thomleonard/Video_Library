from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'Series'
urlpatterns = [
    url(r'^$', views.library, name='library'),
    url(r'^tvshow_(?P<tvshow_pk>\d+)/$',
    	views.tvshow_page, name='tvshow_page'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
