from django.conf.urls import url

from drf_batch_example import views

urlpatterns = [
    url('test', views.TestView.as_view()),
]
