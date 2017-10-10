DRF batch requests
=====================

Quick start
-----------


examples:
```
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
```

using file uploading
```
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
```


Future features:

- add support for requests pipelining. use responses as arguments to next requests (done)
- build graph based on requests dependencies & run simultaneously independent.
- switchable atomic support. true - all fails if something wrong. else - fail only dependent (can be very hard to support on front-end side, but for now seems as good feature)
- use native django. we don't use complicated things that require drf for work. all can be done with "naked" django.
- support files uploading (done)
