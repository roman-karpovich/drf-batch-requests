from django.conf.urls import url, include

from tests import views

urlpatterns = [
    url(r'batch/', include('drf_batch_requests.urls', namespace='drf_batch')),
    url(r'test/', views.TestAPIView.as_view()),
    url(r'test_fbv/', views.test_fbv),
]
