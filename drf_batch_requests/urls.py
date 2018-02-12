try:
    from django.conf.urls import url
except:
    # django 2.0
    from django.urls import re_path as url

from drf_batch_requests import views

app_name = 'drt_batch_requests'

urlpatterns = [
    url('^', views.BatchView.as_view())
]
