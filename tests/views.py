from django.http import JsonResponse
from django.http.response import HttpResponse as DjangoResponse
from django.views.generic import View

from rest_framework.response import Response
from rest_framework.views import APIView


class TestAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return self.finalize_response(request, Response({
            'data': [
                {'id': 1, 'some_data': 'foo'},
                {'id': 2, 'some_data': 'bar'},
                {'id': 3, 'some_data': 'baz'},
            ],
            'page': 1,
            'get': request.query_params
        }))

    def post(self, request, *args, **kwargs):
        return self.finalize_response(request, Response({'data': request.data.get('data')}))


def test_fbv(request):
    if request.method == 'POST':
        return JsonResponse(request.POST)
    else:
        return JsonResponse({'field1': 'field1_value', 'field2': 'field2_value'})


class TestFilesAPIView(APIView):
    def post(self, request, *args, **kwargs):
        return self.finalize_response(request, Response({
            'files': {
                key: {
                    'name': attachment.name,
                    'size': attachment.size
                }
                for key, attachment in request.FILES.items()
            }
        }))


class SimpleView(View):
    def get(self, request):
        return DjangoResponse('test non-json output')
