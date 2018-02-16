from django.core.handlers.base import BaseHandler
from rest_framework.status import is_success

from drf_batch_requests.backends.base import RequestsConsumeBaseBackend


class SyncRequestsConsumeBackend(RequestsConsumeBaseBackend):
    def __init__(self):
        self.responses = {}

    # todo: from this point i think we can consume requests pack
    def consume_request(self, request, start_callback=None, success_callback=None, fail_callback=None):
        start_callback() if start_callback else None

        handler = BaseHandler()
        handler.load_middleware()

        response = handler.get_response(request)

        if is_success(response.status_code):
            success_callback() if success_callback else None
        else:
            fail_callback() if fail_callback else None

        self.responses[request] = response

        return True
