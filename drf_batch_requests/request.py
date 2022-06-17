import json
import re
from io import BytesIO
from urllib.parse import urlsplit

from django.http import HttpRequest
from django.http.request import QueryDict

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_str as force_text

from rest_framework.exceptions import ValidationError

from drf_batch_requests.exceptions import RequestAttributeError
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

        split_url = urlsplit(request_data['relative_url'])
        self.path_info = self.path = split_url.path

        self.GET = QueryDict(split_url.query)
        self._set_headers(request, request_data.get('headers', {}))
        self.COOKIES = request.COOKIES

    # Standard WSGI supported headers
    # (are not prefixed with HTTP_)
    _wsgi_headers = ["content_length", "content_type", "query_string",
                     "remote_addr", "remote_host", "remote_user",
                     "request_method", "server_name", "server_port"]

    def _set_headers(self, request, headers):
        """
        Inherit headers from batch request by default.
        Override with values given in subrequest.
        """
        self.META = request.META if request is not None else {}
        if headers is not None:
            self.META.update(self._transform_headers(headers))

    def _transform_headers(self, headers):
        """
        For every header:
        - replace - to _
        - prepend http_ if necessary
        - convert to uppercase
        """
        result = {}
        for header, value in headers.items():
            header = header.replace("-", "_")
            header = "http_{header}".format(header=header) \
                     if header.lower() not in self._wsgi_headers \
                     else header
            result.update({header.upper(): value})
        return result


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
            value = value if isinstance(value, str) else json.dumps(value)
            body += '--{}\r\nContent-Disposition: form-data; name="{}"\r\n\r\n{}\r\n'.format(boundary, key, value)

        if files:
            for key, attachment in files.items():
                attachment.seek(0)
                attachment_body_part = '--{0}\r\nContent-Disposition: form-data; name="{1}"; filename="{2}"\r\n' \
                                       'Content-Type: {3}\r\n' \
                                       'Content-Transfer-Encoding: binary\r\n\r\n{4}\r\n'
                body += attachment_body_part.format(
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
                self.named_responses[url_param[1]].data,
                url_param[2].split('.')
            )

            if result is None:
                raise RequestAttributeError('Empty result for {}'.format(url_param[2]))

            if isinstance(result, list):
                result = ','.join(map(str, result))

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
        elif isinstance(obj, str):
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
