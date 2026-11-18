from datetime import date, timedelta
from typing import Any

from rest_framework import serializers

from planning_rules.models import DayOffRequest, RulesConfig, Shift, ShiftKind
from schedules.models import Shift as StoredShift
from schedules.models import StaffMember


class ShiftSerializer(serializers.Serializer):
    staff_id = serializers.CharField()
    start = serializers.DateTimeField(input_formats=["%Y-%m-%dT%H:%M:%S"])
    end = serializers.DateTimeField(input_formats=["%Y-%m-%dT%H:%M:%S"])
    kind = serializers.ChoiceField(choices=[kind.value for kind in ShiftKind])

    def validate(self, attrs: dict[str, Any]) -> Shift:
        """Construit le poste du moteur à partir des champs validés.

        La règle « un poste finit après son début » reste écrite dans `Shift` : sa `ValueError`
        devient ici une erreur de validation.
        """

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

    def validate(self, attrs: dict[str, Any]) -> DayOffRequest:
        """Construit la demande de repos du moteur à partir des champs validés."""

        return DayOffRequest(**attrs)


class RulesConfigSerializer(serializers.Serializer):
    min_daily_rest = serializers.DurationField(required=False, min_value=timedelta(0))
    max_consecutive_nights = serializers.IntegerField(required=False, min_value=1)
    max_weekly_duration = serializers.DurationField(required=False, min_value=timedelta(0))

    def validate(self, attrs: dict[str, Any]) -> RulesConfig:
        """Construit la configuration du moteur à partir des seuils fournis.

        Un seuil absent garde la valeur par défaut de `RulesConfig`.
        """

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


class StaffMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffMember
        fields = ["code", "full_name"]


class PeriodSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()

    def validate(self, attrs: dict[str, date]) -> dict[str, date]:
        """Refuse une période qui finit avant de commencer.

        Une période d'un seul jour, dont le début et la fin sont égaux, reste valable.
        """

        if attrs["end"] < attrs["start"]:
            raise serializers.ValidationError("La période doit se terminer après son début.")
        return attrs


class StoredShiftSerializer(serializers.ModelSerializer):
    staff = serializers.SlugRelatedField(slug_field="code", read_only=True)

    class Meta:
        model = StoredShift
        fields = ["id", "staff", "start", "end", "kind"]
