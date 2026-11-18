from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeBoundary, RangeOperators
from django.db import models

from planning_rules import models as engine


class TsTzRange(models.Func):
    """Intervalle PostgreSQL entre deux dates, début inclus et fin exclue."""

    function = "TSTZRANGE"
    output_field = DateTimeRangeField()


class StaffMember(models.Model):
    code = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=200)

    class Meta:
        ordering = ["code"]


class Shift(models.Model):
    staff = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name="shifts")
    start = models.DateTimeField()
    end = models.DateTimeField()
    kind = models.CharField(
        max_length=4, choices=[(kind.value, kind.value) for kind in engine.ShiftKind]
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end__gt=models.F("start")),
                name="shift_ends_after_start",
            ),
            ExclusionConstraint(
                name="exclude_overlapping_shifts",
                expressions=[
                    (TsTzRange("start", "end", RangeBoundary()), RangeOperators.OVERLAPS),
                    ("staff", RangeOperators.EQUAL),
                ],
            ),
        ]

    def to_engine(self) -> engine.Shift:
        """Convertit le poste enregistré en poste du moteur de règles."""

        return engine.Shift(
            staff_id=self.staff.code,
            start=self.start,
            end=self.end,
            kind=engine.ShiftKind(self.kind),
        )


class DayOffRequest(models.Model):
    staff = models.ForeignKey(
        StaffMember, on_delete=models.CASCADE, related_name="day_off_requests"
    )
    day = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["staff", "day"], name="unique_day_off_request"),
        ]

    def to_engine(self) -> engine.DayOffRequest:
        """Convertit la demande de repos enregistrée en une demande de repos du moteur de règles."""

        return engine.DayOffRequest(
            staff_id=self.staff.code,
            day=self.day,
        )
