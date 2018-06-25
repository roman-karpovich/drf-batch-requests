from django.utils.encoding import force_text

from drf_batch_requests.exceptions import RequestAttributeError

try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
     from urlparse import urlparse, parse_qs

from django.http import HttpRequest

import re
import json

from django.utils import six
from django.utils.six import BytesIO
from rest_framework.exceptions import ValidationError

from drf_batch_requests.serializers import BatchRequestSerializer
from drf_batch_requests.utils import get_attribute


class BatchRequest(HttpRequest):
    def __init__(self, request, request_data):
        super(BatchRequest, self).__init__()
        self.name = request_data.get('name')
        self.omit_response_on_success = request_data.get('omit_response_on_success', False)

        self._stream = BytesIO(request_data['_body'].encode('utf-8'))
        self._read_started = False

        self.method = request_data['method']
        self.path_info = self.path = request_data['relative_url']
        self.META = request.META
        self.COOKIES = request.COOKIES
        self.GET = parse_qs(urlparse(self.path_info).query)


class BatchRequestsFactory(object):
    response_variable_regex = re.compile(r'({result=(?P<name>[\w\d_]+):\$\.(?P<value>[\w\d_.*]+)})')

    def __init__(self, request):
        self.request = request
        self.request_serializer = BatchRequestSerializer(data=request.data)
        self.request_serializer.is_valid(raise_exception=True)
        self.update_soft_dependencies()

        self.named_responses = {}

    def update_soft_dependencies(self):
        for request_data in self.request_serializer.validated_data['batch']:
            parents = request_data.get('depends_on', [])

            for part in request_data.values():
                params = re.findall(
                    self.response_variable_regex, force_text(part)
                )

                parents.extend(map(lambda param: param[1], params or []))

            request_data['depends_on'] = set(parents)

    def _prepare_formdata_body(self, data, files=None):
        if not data and not files:
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
            self.response_variable_regex, attr
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

            if result is None:
                raise RequestAttributeError('Empty result for {}'.format(url_param[2]))

            if isinstance(result, list):
                result = ','.join(map(six.text_type, result))

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

    def get_requests_data(self):
        return self.request_serializer.validated_data['batch']

    def generate_request(self, request_data):
        request_data['data'] = self.updated_obj(request_data['data'])
        request_data['relative_url'] = self._process_attr(request_data['relative_url'])

        if self.request.content_type.startswith('multipart/form-data'):
            request_data['_body'] = self._prepare_formdata_body(request_data['data'],
                                                                files=request_data.get('files', {}))
        elif self.request.content_type.startswith('application/x-www-form-urlencoded'):
            request_data['_body'] = self._prepare_urlencoded_body(request_data['data'])
        elif self.request.content_type.startswith('application/json'):
            request_data['_body'] = self._prepare_json_body(request_data['data'])
        else:
            raise ValidationError('Unsupported content type')

        return BatchRequest(self.request, request_data)
