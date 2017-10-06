import json
import itertools

from django.core.files import File
from django.utils import six

from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class SingleRequestSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    method = serializers.CharField()
    relative_url = serializers.CharField()
    body = serializers.JSONField(required=False, default={})
    attached_files = serializers.ListField(child=serializers.CharField(), required=False)
    data = serializers.SerializerMethodField()

    def validate_relative_url(self, value):
        if not value.startswith('/'):
            raise self.fail('Url should start with /')

        return value

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


class BatchRequestSerializer(serializers.Serializer):
    batch = serializers.JSONField()
    files = serializers.SerializerMethodField()

    def get_files(self, attrs=None):
        return {fn: f for fn, f in self.initial_data.items() if isinstance(f, File)}

    def validate_batch(self, value):
        if not isinstance(value, list):
            raise ValidationError('List of requests should be provided to do batch')

        r_serializers = list(map(lambda d: SingleRequestSerializer(data=d), value))

        errors = []
        for serializer in r_serializers:
            serializer.is_valid()
            errors.append(serializer.errors)
        if any(errors):
            raise ValidationError(errors)

        return [s.data for s in r_serializers]

    def validate(self, attrs):
        attrs = super(BatchRequestSerializer, self).validate(attrs)

        files_in_use = set(itertools.chain(*map(lambda r: r.get('attached_files', []), attrs['batch'])))
        missing_files = files_in_use - set(self.get_files().keys())
        if missing_files:
            raise ValidationError('Some of files are not provided: {}'.format(', '.join(missing_files)))

        return attrs
