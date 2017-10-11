from django.conf.urls import include, url

urlpatterns = [
    url(r'^batch/', include('drf_batch.urls', namespace='drf_batch')),
    url(r'^example/', include('drf_batch_example.urls', namespace='drf_batch_example')),
    # todo: remove
    url(r'^', include('tests.urls')),
]
