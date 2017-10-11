import json

from .mixins import APITestCase


class BaseTestCase(APITestCase):
    def test_json_batch(self):
        batch = [
            {
                "method": "GET",
                "relative_url": "/tests/test/",
                "name": "request1"
            },
            {
                "method": "GET",
                "relative_url": "/tests/test/?ids={result=request1:$.data.*.id}"
            }
        ]

        responses = self.forced_auth_req('post', '/batch/', data={'batch': batch})
        responses_data = list(map(lambda r: json.loads(r['body']), responses.data))

        self.assertIn('ids', responses_data[1]['get'])
        self.assertEqual(
            responses_data[1]['get']['ids'],
            ','.join(map(lambda o: str(o['id']), responses_data[0]['data']))
        )
