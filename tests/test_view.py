import json

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from tests.mixins import APITestCase


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
        self.assertEqual(responses.status_code, status.HTTP_200_OK, msg=responses.data)

        responses_data = [json.loads(r['body']) for r in responses.data]

        self.assertIn('ids', responses_data[1]['get'])
        self.assertEqual(
            responses_data[1]['get']['ids'],
            ','.join([str(o['id']) for o in responses_data[0]['data']])
        )

    def test_multipart_simple_request(self):
        batch = [
            {
                "method": "GET",
                "relative_url": "/tests/test/"
            }
        ]

        responses = self.forced_auth_req(
            'post', '/batch/',
            data={'batch': json.dumps(batch)},
            request_format='multipart',
        )
        self.assertEqual(responses.status_code, status.HTTP_200_OK, msg=responses.data)

        responses_data = list(map(lambda r: json.loads(r['body']), responses.data))

        self.assertIn('data', responses_data[0])

    def test_multipart_files_upload(self):
        batch = [
            {
                "method": "POST",
                "relative_url": "/tests/test-files/",
                "attached_files": {
                    "file": "file1",
                    "second_file": 'file2'
                }
            }
        ]

        responses = self.forced_auth_req(
            'post', '/batch/',
            data={
                'batch': json.dumps(batch),
                'file1': SimpleUploadedFile('hello_world.txt', u'hello world!'.encode('utf-8')),
                'file2': SimpleUploadedFile('second file.txt', u'test!'.encode('utf-8')),
            },
            request_format='multipart',
        )
        self.assertEqual(responses.status_code, status.HTTP_200_OK, msg=responses.data)

        responses_data = list(map(lambda r: json.loads(r['body']), responses.data))
        self.assertIn('files', responses_data[0])
        self.assertListEqual(sorted(['file', 'second_file']), sorted(list(responses_data[0]['files'].keys())))
        self.assertListEqual(
            sorted(['hello_world.txt', 'second file.txt']),
            sorted([a['name'] for a in responses_data[0]['files'].values()])
        )

    def test_non_json(self):
        responses = self.forced_auth_req(
            'post', '/batch/',
            data={
                'batch': [
                    {
                        'method': 'GET',
                        'relative_url': '/test-non-json/'
                    }
                ]
            }
        )

        self.assertEqual(responses.status_code, status.HTTP_200_OK, msg=responses.data)
        self.assertEqual(responses.data[0]['body'], 'test non-json output')
