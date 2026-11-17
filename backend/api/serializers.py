from rest_framework import serializers


class CheckScheduleSerializer(serializers.Serializer):
    shifts = serializers.ListField()
