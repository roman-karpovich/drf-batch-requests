from importlib import import_module

from django.db import transaction

from rest_framework.response import Response
from rest_framework.views import APIView

from drf_batch_requests import settings as app_settings
from drf_batch_requests.exceptions import RequestAttributeError
from drf_batch_requests.graph import RequestGraph
from drf_batch_requests.request import BatchRequestsFactory
from drf_batch_requests.response import BatchResponse, DummyBatchResponse, ResponseHeader
from drf_batch_requests.utils import generate_node_callback

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


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
                except RequestAttributeError:
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

                header_items = response.items()

                result = BatchResponse(
                    current_request.name,
                    response.status_code,
                    response.content.decode('utf-8'),
                    headers=[
                        ResponseHeader(key, value)
                        for key, value in header_items
                    ],
                    omit_response_on_success=current_request.omit_response_on_success,
                    status_text=response.reason_phrase
                )

                if current_request.name:
                    requests_factory.named_responses[current_request.name] = result

                responses[current_request.name] = result.to_dict()

            if is_completed:
                break

        ordered_responses = [responses.get(name, DummyBatchResponse(name).to_dict()) for name in ordered_names]
        return self.finalize_response(request, Response(ordered_responses))
