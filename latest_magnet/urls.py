from django.conf.urls import url

from . import views

app_name = 'latest_magnet'
urlpatterns = [
    url(r'^$', views.search, name='search'),
]