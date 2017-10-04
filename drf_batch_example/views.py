import json

import re

from django.core.handlers.base import BaseHandler
from django.http import JsonResponse, HttpRequest
from django.utils import six
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
    def _process_attr(self, attr):
        params = re.findall(
            r'({result=(?P<name>\w+):\$\.(?P<value>[a-zA-Z0-9.*]+)})', attr
        )
        if not params:
            return attr

        for url_param in params:
            if url_param[1] not in self.named_responses:
                raise ValidationError('Named request {0} is missing'.format(url_param[1]))

            result = get_attribute(
                self.named_responses[url_param[1]]['data'],
                url_param[2].split('.')
            )
            if isinstance(result, list):
                result = ','.join(result)

            if attr == url_param[0]:
                attr = result
            else:
                attr = attr.replace(url_param[0], str(result))

        return attr

    def updated_obj(self, obj):
        """
        For now, i'll update only dict values. Later it can be used for keys/single values/etc
        :param obj: dict
        :return: dict
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                obj[key] = self.updated_obj(value)
        elif isinstance(obj, six.string_types):
            return self._process_attr(obj)

        return obj

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
            relative_url = self._process_attr(request_data['relative_url'])

            current_request.path_info = current_request.path = relative_url
            current_request.META = request.META

            if 'body' in request_data:
                request_body = json.dumps(self.updated_obj(json.loads(request_data['body'])))
            else:
                request_body = ''

            current_request._stream = BytesIO(request_body.encode('utf-8'))
            current_request._read_started = False

            response = handler.get_response(current_request)
            result = {
                'code': response.status_code,
                'headers': [
                    {'name': key, 'value': value}
                    for key, value in response._headers.values()
                ],
                'body': response.content.decode('utf-8'),
                'data': json.loads(response.content.decode('utf-8'))
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
