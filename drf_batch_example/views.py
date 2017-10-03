import json

import re

from django.core.handlers.base import BaseHandler
from django.http import JsonResponse, HttpRequest
from django.utils.six import BytesIO
from rest_framework.exceptions import ValidationError
from rest_framework.status import is_success

from rest_framework.views import APIView


def get_attribute(instance, attrs):
    for attr in attrs:
        if instance is None:
            return None

        if attr == '*':
            # todo: maybe there should be some kind of filtering?
            continue

        if isinstance(instance, list):
            instance = list(map(lambda i: i[attr], instance))
        else:
            instance = instance[attr]
    return instance


class BatchView(APIView):
    def _process_url(self, relative_url):
        url_params = re.findall(
            r'({result=(?P<name>\w+):\$\.(?P<value>[a-zA-Z0-9.*]+)})', relative_url
        )
        if not url_params:
            return relative_url

        for url_param in url_params:
            if url_param[1] not in self.named_responses:
                raise ValidationError('Named request {0} is missing'.format(url_param[1]))

            result = get_attribute(
                json.loads(self.named_responses[url_param[1]]['body']),
                url_param[2].split('.')
            )
            if isinstance(result, list):
                result = ','.join(result)

            relative_url = relative_url.replace(url_param[0], str(result))

        return relative_url

    def post(self, request, *args, **kwargs):
        self.requests = request.data

        if not isinstance(self.requests, list):
            raise ValidationError('List of requests should be provided to do batch')

        self.responses = []
        self.named_responses = {}

        for request_data in self.requests:
            handler = BaseHandler()
            handler.load_middleware()
            current_request = HttpRequest()

            # todo: create serializer for method, body, etc
            current_request.method = request_data['method']

            # todo: validate relative_url
            relative_url = self._process_url(request_data['relative_url'])

            current_request.path_info = current_request.path = relative_url
            current_request.META = request.META

            stream = BytesIO(request_data.get('body', '').encode('utf-8'))
            current_request._stream = stream
            current_request._read_started = False

            response = handler.get_response(current_request)
            result = {
                'code': response.status_code,
                'headers': [
                    {'name': key, 'value': value}
                    for key, value in response._headers.values()
                ],
                'body': response.content.decode('utf-8')
            }

            if not is_success(response.status_code) or \
               is_success(response.status_code) and not request_data.get('omit_response_on_success'):
                result['return_body'] = True

            if 'name' in request_data:
                self.named_responses[request_data['name']] = result

            self.responses.append(result)

        return self.finalize_response(request, JsonResponse(self.responses, safe=False))


class TestView(APIView):
    def get(self, request, *args, **kwargs):
        return self.finalize_response(request, JsonResponse({
            'id': 1,
            'data': [
                {'id': '1'},
                {'id': '2'},
                {'id': '3'},
                {'id': '4'},
            ]
        }))

    def post(self, request, *args, **kwargs):
        return self.finalize_response(request, JsonResponse({'data': request.data.get('data')}))

# todo: add CBV and FBV
