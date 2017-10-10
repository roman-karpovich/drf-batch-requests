import json
import re

from django.core.handlers.base import BaseHandler
from django.http import HttpRequest, JsonResponse
from django.utils import six
from django.utils.six import BytesIO

from rest_framework.exceptions import ValidationError
from rest_framework.status import is_success, is_client_error
from rest_framework.views import APIView

from .serializers import BatchRequestSerializer
from .utils import get_attribute


class BatchView(APIView):
    def _prepare_formdata_body(self, data, files=None):
        if not data:
            return ''

        match = re.search(r'boundary=(?P<boundary>.+)', self.request.content_type)
        assert match
        boundary = match.groupdict()['boundary']
        body = ''
        for key, value in data.items():
            value = value if isinstance(value, six.string_types) else json.dumps(value)
            body += '--{}\r\nContent-Disposition: form-data; name="{}"\r\n\r\n{}\r\n'.format(boundary, key, value)

        if files:
            for key, attachment in files.items():
                attachment.seek(0)
                body += '--{}\r\nContent-Disposition: form-data; name="{}"; filename="{}"\r\n' \
                        'Content-Type: {}\r\n' \
                        'Content-Transfer-Encoding: binary\r\n\r\n{}\r\n'.format(
                    boundary, key, attachment.name, attachment.content_type, attachment.read()
                )

        body += '--{}--\r\n'.format(boundary)
        return body

    def _prepare_urlencoded_body(self, data):
        raise NotImplementedError

    def _prepare_json_body(self, data):
        return json.dumps(data)

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
        request_serializer = BatchRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        self.responses = []
        self.named_responses = {}

        for request_data in request_serializer.data['batch']:
            handler = BaseHandler()
            handler.load_middleware()
            current_request = HttpRequest()

            current_request.method = request_data['method']
            current_request.path_info = current_request.path = self._process_attr(request_data['relative_url'])
            current_request.META = request.META

            request_data['data'] = self.updated_obj(request_data['data'])

            if request.content_type.startswith('multipart/form-data'):
                body = self._prepare_formdata_body(request_data['data'], files=request_data.get('files', {}))
            elif request.content_type.startswith('application/x-www-form-urlencoded'):
                body = self._prepare_urlencoded_body(request_data['data'])
            elif request.content_type.startswith('application/json'):
                body = self._prepare_json_body(request_data['data'])
            else:
                raise ValidationError('Unsupported content type')

            current_request._stream = BytesIO(body.encode('utf-8'))
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

        return self.finalize_response(request, JsonResponse(self.responses, safe=False))
