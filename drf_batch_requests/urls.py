from django.conf.urls import url

from drf_batch_requests import views


urlpatterns = [
    url('^', views.BatchView.as_view())
]
