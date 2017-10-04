from django.conf.urls import url

from . import views


urlpatterns = [
    url('batch', views.BatchView.as_view())
]
