from django.conf.urls import include, url

urlpatterns = [
    url(r'^', include('drf_batch_example.urls', namespace='drf_batch_example')),
]
