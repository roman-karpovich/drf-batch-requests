DRF batch requests
==================

|PyPI version| |Travis CI| |Coverage Status| |Code Health| |Python
Versions| |Implementation|

Quick start
-----------

examples:

::

        curl -X POST \
          http://127.0.0.1:8000/batch/ \
          -H 'cache-control: no-cache' \
          -H 'content-type: application/json' \
          -d '{"batch": [
            {
                "method": "get",
                "relative_url": "/test/",
                "name": "yolo"
            },
            {
                "method": "post",
                "relative_url": "/test/?id={result=yolo:$.id}&ids={result=yolo:$.data.*.id}",
                "body": {"data": {"id": "{result=yolo:$.id}", "ids": "{result=yolo:$.data.*.id}"}, "test": "yolo"}
            },
            {
                "method": "post",
                "relative_url": "/test/",
                "body": "{\"data\": 42}",
                "omit_response_on_success": true
            },
            {
                "method": "options",
                "relative_url": "/test/"
            }
        ]
        }'

using file uploading

::

        curl -X POST \
          http://127.0.0.1:8000/batch/ \
          -H 'cache-control: no-cache' \
          -H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
          -F 'batch=[
            {
                "method": "get",
                "relative_url": "/test/",
                "name": "yolo"
            },
            {
                "method": "post",
                "relative_url": "/test/?id={result=yolo:$.id}&ids={result=yolo:$.data.*.id}",
                "body": {"data": "{result=yolo:$.data.*.id}", "test": "yolo"},
                "attached_files":{"file": "a.jpg"}
            },
            {
                "method": "post",
                "relative_url": "/test/",
                "body": "{\"data\": 42}",
                "omit_response_on_success": true,
                "attached_files":["a.jpg", "b.png"]
            },
            {
                "method": "options",
                "relative_url": "/test/"
            }
        ]' \
          -F b.png=@2476.png \
          -F a.jpg=@check_133.pdf

Future features:

-  add support for requests pipelining. use responses as arguments to
   next requests (done)
-  build graph based on requests dependencies & run simultaneously
   independent.
-  [STRIKEOUT:switchable atomic support. true - all fails if something
   wrong. else - fail only dependent (can be very hard to support on
   front-end side, but for now seems as good feature)] run all requests
   in single transaction. (done)
-  [STRIKEOUT:use native django. we don't use complicated things that
   require drf for work. all can be done with "naked" django.] (since we
   validate requests with drf serializers, it's better to leave as it
   is).
-  support files uploading (done)

Dependencies:

-  Django starting from 2.2
-  Django rest framework

.. |PyPI version| image:: https://badge.fury.io/py/drf-batch-requests.svg
   :target: https://badge.fury.io/py/drf-batch-requests
.. |Travis CI| image:: https://travis-ci.org/roman-karpovich/drf-batch-requests.svg?branch=master
   :target: https://travis-ci.org/roman-karpovich/drf-batch-requests
.. |Coverage Status| image:: https://coveralls.io/repos/github/roman-karpovich/drf-batch-requests/badge.svg?branch=master
   :target: https://coveralls.io/github/roman-karpovich/drf-batch-requests?branch=master
.. |Code Health| image:: https://landscape.io/github/roman-karpovich/drf-batch-requests/master/landscape.svg?style=flat
   :target: https://landscape.io/github/roman-karpovich/drf-batch-requests/master
.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/drf-batch-requests.svg?style=flat-square
   :target: https://pypi.python.org/pypi/drf-batch-requests
.. |Implementation| image:: https://img.shields.io/pypi/implementation/drf-batch-requests.svg?style=flat-square
   :target: https://pypi.python.org/pypi/drf-batch-requests
