import json
from json import JSONDecodeError
from typing import Iterable

from rest_framework.status import is_success


class ResponseHeader:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    def to_dict(self):
        return {
            'key': self.name,
            'value': self.value,
        }


class BatchResponse:
    name: str
    code: int
    code_text: str
    headers: Iterable[ResponseHeader]
    body: str
    _data: dict
    _return_body: bool = True

    def __init__(self, name: str, status_code: int, body: str, headers: Iterable[ResponseHeader] = None,
                 omit_response_on_success: bool = False, status_text: str = None):
        self.name = name
        self.status_code = status_code
        self.status_text = status_text
        self.body = body
        self.headers = headers or []
        self.omit_response_on_success = omit_response_on_success

        if is_success(self.status_code):
            try:
                self._data = json.loads(self.body)
            except JSONDecodeError:
                self._data = {}

        if is_success(self.status_code) and self.omit_response_on_success:
            self._return_body = False

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'code': self.status_code,
            'code_text': self.status_text,
            'headers': [h.to_dict() for h in self.headers],
            'body': self.body,
        }

    @property
    def data(self):
        return self._data


class DummyBatchResponse(BatchResponse):
    def __init__(self, name: str):
        super().__init__(name, 418, '')
