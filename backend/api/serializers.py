from rest_framework import serializers

from planning_rules.models import Shift, ShiftKind


class ShiftSerializer(serializers.Serializer):
    staff_id = serializers.CharField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    kind = serializers.ChoiceField(choices=[kind.value for kind in ShiftKind])

    def validate(self, attrs):
        try:
            return Shift(
                staff_id=attrs["staff_id"],
                start=attrs["start"],
                end=attrs["end"],
                kind=ShiftKind(attrs["kind"]),
            )
        except ValueError as error:
            raise serializers.ValidationError(str(error)) from error


class CheckScheduleSerializer(serializers.Serializer):
    shifts = ShiftSerializer(many=True)


class ViolationSerializer(serializers.Serializer):
    rule = serializers.CharField()
    category = serializers.CharField(source="category.value")
    staff_id = serializers.CharField()
    day = serializers.DateField()
    message = serializers.CharField()
