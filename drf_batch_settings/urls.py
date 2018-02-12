try:
    from django.conf.urls import url, include
except:
    # django 2.0
    from django.urls import re_path as url, include

urlpatterns = [
    url(r'^batch/', include('drf_batch_requests.urls', namespace='drf_batch')),
    url(r'^example/', include('drf_batch_example.urls', namespace='drf_batch_example')),
]
