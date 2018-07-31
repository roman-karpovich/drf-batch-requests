from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory
from drf_batch_requests.request import BatchRequest


class RequestTest(SimpleTestCase):

    def test_subrequest_headers(self):
        # Arrange
        data = {
            'method': 'get',
            'relative_url': '/test/',
            'headers': {
                'header-1': 'whatever',
                'Content-Length': 56,
            },
            '_body': ''
        }
        request = APIRequestFactory().post('/test')
        # Act
        result = BatchRequest(request, data)
        # Assert
        self.assertIn('HTTP_HEADER_1', result.META)
        self.assertIn('CONTENT_LENGTH', result.META)