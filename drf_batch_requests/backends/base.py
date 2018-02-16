class RequestsConsumeBaseBackend(object):
    def consume_request(self, request, start_callback=None, success_callback=None, fail_callback=None):
        raise NotImplementedError
