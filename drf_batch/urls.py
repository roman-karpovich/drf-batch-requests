from django.conf.urls import url

from . import views


urlpatterns = [
    url('^', views.BatchView.as_view())
]
