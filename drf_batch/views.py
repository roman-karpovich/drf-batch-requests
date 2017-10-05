import json
import re

from django.core.handlers.base import BaseHandler
from django.http import HttpRequest, JsonResponse
from django.utils import six
from django.utils.six import BytesIO

from rest_framework.exceptions import ValidationError
from rest_framework.status import is_success, is_client_error
from rest_framework.views import APIView

from .serializers import JSONBatchRequestSerializer
from .utils import get_attribute


class BatchView(APIView):
    def _process_attr(self, attr):
        params = re.findall(
            r'({result=(?P<name>\w+):\$\.(?P<value>[a-zA-Z0-9.*]+)})', attr
        )
        if not params:
            return attr

        for url_param in params:
            if url_param[1] not in self.named_responses:
                raise ValidationError('Named request {} is missing'.format(url_param[1]))

            result = get_attribute(
                self.named_responses[url_param[1]]['_data'],
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
        errors = {}

        for i, batch_request in enumerate(self.requests):
            handler = BaseHandler()
            handler.load_middleware()
            current_request = HttpRequest()

            # todo: switch serializer in dependency of content type
            request_serializer = JSONBatchRequestSerializer(data=batch_request)
            if not request_serializer.is_valid(raise_exception=False):
                errors[i] = request_serializer.errors
                break

            request_data = request_serializer.data

            current_request.method = request_data['method']
            current_request.path_info = current_request.path = self._process_attr(request_data['relative_url'])
            current_request.META = request.META

            # todo: if body contains something other than json, more logic needed
            current_request._stream = BytesIO(json.dumps(self.updated_obj(request_data['data'])).encode('utf-8'))
            current_request._read_started = False

            response = handler.get_response(current_request)
            result = {
                'code': response.status_code,
                'headers': [
                    {'name': key, 'value': value}
                    for key, value in response._headers.values()
                ],
                'body': response.content.decode('utf-8'),
            }

            if is_success(response.status_code) or is_client_error(response.status_code):
                result['_data'] = json.loads(result['body'])

            if not is_success(response.status_code) or \
               is_success(response.status_code) and not request_data.get('omit_response_on_success'):
                result['return_body'] = True

            if 'name' in request_data:
                self.named_responses[request_data['name']] = result

            self.responses.append({k: v for k, v in result.items() if not k.startswith('_')})

        if errors:
            raise ValidationError(errors)

        return self.finalize_response(request, JsonResponse(self.responses, safe=False))
