try:
    from django.conf.urls import url
except ImportError:
    # django 2.0
    from django.urls import re_path as url

from drf_batch_example import views

app_name = 'drf_batch_requests_tests'

urlpatterns = [
    url('test', views.TestView.as_view()),
]
