from django.core.handlers.base import BaseHandler
from django.http import JsonResponse, HttpRequest
from django.utils.six import BytesIO

from rest_framework.views import APIView


class BatchView(APIView):
    def post(self, request, *args, **kwargs):
        # todo: raise validation error
        assert 'batch' in request.data, 'You should provide data for batch request'

        requests = request.data['batch']

        # todo: raise validation error
        assert isinstance(requests, list), 'List of requests should be provided to do batch'

        responses = []

        for data in requests:
            handler = BaseHandler()
            handler.load_middleware()
            current_request = HttpRequest()

            # todo: create serializer for method, body, etc
            current_request.method = data['method']

            # todo: validate relative_url
            current_request.path_info = current_request.path = data['relative_url']
            current_request.META = request.META

            stream = BytesIO(data.get('body', '').encode('utf-8'))
            current_request._stream = stream
            current_request._read_started = False

            response = handler.get_response(current_request)
            result = {
                'code': response.status_code,
            }

            # todo: make normal check instead of simple 200
            if response.status_code != 200 or response.status_code == 200 and not data.get('omit_response_on_success'):
                result['body'] = response.content.decode('utf-8')

            responses.append(result)

        return self.finalize_response(request, JsonResponse(responses, safe=False))


class TestView(APIView):
    def get(self, request, *args, **kwargs):
        return self.finalize_response(request, JsonResponse({'id': '1'}))

    def post(self, request, *args, **kwargs):
        return self.finalize_response(request, JsonResponse({'data': request.data.get('data')}))

# todo: add CBV and FBV
