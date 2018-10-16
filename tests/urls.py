try:
    from django.conf.urls import url, include
except:
    # django 2.0
    from django.urls import re_path as url, include

from tests import views

urlpatterns = [
    url('batch/', include('drf_batch_requests.urls', namespace='drf_batch')),
    url('test/', views.TestAPIView.as_view()),
    url('test_fbv/', views.test_fbv),
    url('test-files/', views.TestFilesAPIView.as_view()),
    url('test-non-json/', views.SimpleView.as_view()),
]
