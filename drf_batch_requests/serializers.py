import json

from django.core.files import File
from django.utils import six

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from drf_batch_requests.utils import generate_random_id


class SingleRequestSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    depends_on = serializers.JSONField(required=False)
    method = serializers.CharField()
    relative_url = serializers.CharField()
    body = serializers.JSONField(required=False, default={})
    # attached files formats: ["a.jpg", "b.png"] - will be attached as it is, {"file": "a.jpg"} - attach as specific key
    attached_files = serializers.JSONField(required=False)
    data = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()

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

    def validate(self, attrs):
        if 'name' not in attrs:
            attrs['name'] = generate_random_id()

        if 'depends_on' in attrs:
            value = attrs['depends_on']
            if not isinstance(value, (six.string_types, list)):
                raise ValidationError({'depends_on': 'Incorrect value provided'})

            if isinstance(value, six.string_types):
                attrs['depends_on'] = [value]

        return attrs

    def get_data(self, data):
        body = data['body']
        if isinstance(body, dict):
            return body

        return json.loads(body)

    def get_files(self, attrs):
        if 'attached_files' not in attrs:
            return []

        attached_files = attrs['attached_files']
        if isinstance(attached_files, dict):
            return {
                key: self.context['parent'].get_files()[attrs['attached_files'][key]] for key in attrs['attached_files']
            }
        elif isinstance(attached_files, list):
            return {
                key: self.context['parent'].get_files()[key] for key in attrs['attached_files']
            }
        else:
            raise ValidationError('Incorrect format.')


class BatchRequestSerializer(serializers.Serializer):
    batch = serializers.JSONField()
    files = serializers.SerializerMethodField()

    def get_files(self, attrs=None):
        return {fn: f for fn, f in self.initial_data.items() if isinstance(f, File)}

    def validate_batch(self, value):
        if not isinstance(value, list):
            raise ValidationError('List of requests should be provided to do batch')

        r_serializers = list(map(lambda d: SingleRequestSerializer(data=d, context={'parent': self}), value))

        errors = []
        for serializer in r_serializers:
            serializer.is_valid()
            errors.append(serializer.errors)
        if any(errors):
            raise ValidationError(errors)

        return [s.data for s in r_serializers]

    def validate(self, attrs):
        attrs = super(BatchRequestSerializer, self).validate(attrs)

        files_in_use = []
        for batch in attrs['batch']:
            if 'attached_files' not in batch:
                continue

            attached_files = batch['attached_files']
            if isinstance(attached_files, dict):
                files_in_use.extend(attached_files.values())
            elif isinstance(attached_files, list):
                files_in_use.extend(attached_files)
            else:
                raise ValidationError({'attached_files': 'Invalid format.'})

        missing_files = set(files_in_use) - set(self.get_files().keys())
        if missing_files:
            raise ValidationError('Some of files are not provided: {}'.format(', '.join(missing_files)))

        return attrs
