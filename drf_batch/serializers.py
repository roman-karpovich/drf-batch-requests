import json

from rest_framework import serializers


class BatchRequestSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    method = serializers.CharField()
    relative_url = serializers.CharField()
    body = serializers.CharField(required=False)

    def validate_relative_url(self, value):
        if not value.startswith('/'):
            raise self.fail('Url should start with /')

        return value


class FormRequestSerializer(BatchRequestSerializer):
    pass


class MultipartRequestSerializer(BatchRequestSerializer):
    pass


class JSONBatchRequestSerializer(BatchRequestSerializer):
    body = serializers.JSONField(required=False, default={})
    data = serializers.SerializerMethodField()

    def validate_body(self, value):
        if isinstance(value, dict):
            return value

        try:
            json.loads(value)
        except (TypeError, ValueError):
            self.fail('invalid')

        return value

    def get_data(self, data):
        body = data['body']
        if isinstance(body, dict):
            return body

        return json.loads(body)
