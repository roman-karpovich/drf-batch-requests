try:
    from django.urls import resolve
except ImportError:
    from django.core.urlresolvers import resolve

from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase as OriginalAPITestCase
from rest_framework.test import force_authenticate


class APITestCase(OriginalAPITestCase):
    """
    Base test case for testing APIs
    """
    maxDiff = None

    def __init__(self, *args, **kwargs):
        super(APITestCase, self).__init__(*args, **kwargs)
        self.user = None

    def forced_auth_req(self, method, url, user=None, data=None, request_format='json', **kwargs):
        """
        Function that allows api methods to be called with forced authentication

        :param method: the HTTP method 'get'/'post'
        :type method: str
        :param url: the relative url to the base domain
        :type url: st
        :param user: optional user if not authenticated as the current user
        :type user: django.contrib.auth.models.User
        :param data: any data that should be passed to the API view
        :type data: dict
        """
        factory = APIRequestFactory()
        view_info = resolve(url)

        data = data or {}
        view = view_info.func
        req_to_call = getattr(factory, method)
        request = req_to_call(url, data, format=request_format, **kwargs)

        user = user or self.user
        force_authenticate(request, user=user)

        response = view(request, *view_info.args, **view_info.kwargs)
        if hasattr(response, 'render'):
            response.render()

        return response
