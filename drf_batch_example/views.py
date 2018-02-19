from django.http import JsonResponse
from rest_framework.views import APIView


class TestView(APIView):
    def get(self, request, *args, **kwargs):
        return self.finalize_response(request, JsonResponse({
            'id': 1,
            'data': [
                {'id': '1'},
                {'id': '2'},
                {'id': '3'},
                {'id': '4'},
            ],
            'empty_argument': None
        }))

    def post(self, request, *args, **kwargs):
        return self.finalize_response(request, JsonResponse({'data': request.data.get('data')}))

# todo: add CBV and FBV
