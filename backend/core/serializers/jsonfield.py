import json
import ast
from rest_framework import serializers


class FlexibleJSONField(serializers.JSONField):
    """
    JSONField that tolerates values coming from multipart/form-data
    where nested JSON may arrive as DRF JSONString objects or plain strings.
    """

    def to_internal_value(self, data):

        # unwrap list from multipart
        if isinstance(data, list) and len(data) == 1:
            data = data[0]

        # already parsed dict
        if isinstance(data, dict):
            return data

        # convert DRF JSONString → normal string
        if not isinstance(data, str):
            try:
                data = str(data)
            except Exception:
                return super().to_internal_value(data)

        data = data.strip()

        # try valid JSON
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            pass

        # try python dict format
        try:
            return ast.literal_eval(data)
        except Exception:
            raise serializers.ValidationError(
                f"Invalid JSON format: {data}"
            )