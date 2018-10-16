import json
from importlib import import_module
from json import JSONDecodeError

from django.db import transaction
from rest_framework.response import Response
from rest_framework.status import is_success
from rest_framework.views import APIView

from drf_batch_requests.exceptions import RequestAttributeError
from drf_batch_requests.graph import RequestGraph
from drf_batch_requests.request import BatchRequestsFactory
from drf_batch_requests import settings as app_settings
from drf_batch_requests.utils import generate_node_callback


class BatchView(APIView):
    permission_classes = []

    def get_requests_consumer_class(self):
        mod, inst = app_settings.REQUESTS_CONSUMER_BACKEND.rsplit('.', 1)
        mod = import_module(mod)
        return getattr(mod, inst)

    def get_requests_consumer(self):
        return self.get_requests_consumer_class()()

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        requests = {}
        responses = {}

        requests_factory = BatchRequestsFactory(request)
        requests_data = requests_factory.get_requests_data()
        ordered_names = list(map(lambda r: r['name'], requests_data))
        requests_graph = RequestGraph(requests_data)

        backend = self.get_requests_consumer()

        while True:
            available_nodes = list(requests_graph.get_current_available_nodes())

            for node in available_nodes:
                try:
                    current_request = requests_factory.generate_request(node.request)
                except RequestAttributeError as ex:
                    # todo: set fail reason
                    node.fail()

                start_callback = generate_node_callback(node, 'start')
                success_callback = generate_node_callback(node, 'success')
                fail_callback = generate_node_callback(node, 'fail')
                if backend.consume_request(current_request, start_callback=start_callback,
                                           success_callback=success_callback, fail_callback=fail_callback):
                    requests[node.name] = current_request

            is_completed = requests_graph.is_completed()

            for current_request, response in backend.responses.items():
                if current_request.name in responses:
                    continue

                result = {
                    'code': response.status_code,
                    'headers': [
                        {'name': key, 'value': value}
                        for key, value in response._headers.values()
                    ],
                    'body': response.content.decode('utf-8'),
                }

                if is_success(response.status_code):
                    try:
                        result['_data'] = json.loads(result['body'])
                    except JSONDecodeError:
                        pass

                if not is_success(response.status_code) or \
                   is_success(response.status_code) and not current_request.omit_response_on_success:
                    result['return_body'] = True

                if current_request.name:
                    requests_factory.named_responses[current_request.name] = result

                responses[current_request.name] = result

            if is_completed:
                break

        ordered_responses = [responses.get(name, {'code': 418}) for name in ordered_names]
        return self.finalize_response(request, Response(ordered_responses))
