from datetime import timedelta

from rest_framework import serializers

from planning_rules.models import DayOffRequest, RulesConfig, Shift, ShiftKind


class ShiftSerializer(serializers.Serializer):
    staff_id = serializers.CharField()
    start = serializers.DateTimeField(input_formats=["%Y-%m-%dT%H:%M:%S"])
    end = serializers.DateTimeField(input_formats=["%Y-%m-%dT%H:%M:%S"])
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


class DayOffRequestSerializer(serializers.Serializer):
    staff_id = serializers.CharField()
    day = serializers.DateField()

    def validate(self, attrs):
        return DayOffRequest(**attrs)


class RulesConfigSerializer(serializers.Serializer):
    min_daily_rest = serializers.DurationField(required=False, min_value=timedelta(0))
    max_consecutive_nights = serializers.IntegerField(required=False, min_value=1)
    max_weekly_duration = serializers.DurationField(required=False, min_value=timedelta(0))

    def validate(self, attrs):
        return RulesConfig(**attrs)


class CheckScheduleSerializer(serializers.Serializer):
    shifts = ShiftSerializer(many=True)
    day_off_requests = DayOffRequestSerializer(many=True, required=False, default=list)
    config = RulesConfigSerializer(required=False)


class ViolationSerializer(serializers.Serializer):
    rule = serializers.CharField()
    category = serializers.CharField(source="category.value")
    staff_id = serializers.CharField()
    day = serializers.DateField()
    message = serializers.CharField()
