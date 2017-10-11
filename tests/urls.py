from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'batch/', include('drf_batch.urls', namespace='drf_batch')),
    url(r'test/', views.TestAPIView.as_view()),
    url(r'test_fbv/', views.test_fbv),
]
