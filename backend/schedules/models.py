from datetime import date

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

    def __str__(self) -> str:
        return f"{self.code} ({self.full_name})"


class ShiftQuerySet(models.QuerySet):
    def starting_between(self, start: date, end: date) -> "ShiftQuerySet":
        """Postes qui commencent entre deux dates, bornes incluses."""

        return self.filter(start__date__range=(start, end)).select_related("staff")


class DayOffRequestQuerySet(models.QuerySet):
    def between(self, start: date, end: date) -> "DayOffRequestQuerySet":
        """Demandes de repos dont le jour tombe entre deux dates, bornes incluses."""

        return self.filter(day__range=(start, end)).select_related("staff")


class Shift(models.Model):
    staff = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name="shifts")
    start = models.DateTimeField()
    end = models.DateTimeField()
    kind = models.CharField(
        max_length=4, choices=[(kind.value, kind.value) for kind in engine.ShiftKind]
    )

    objects = ShiftQuerySet.as_manager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end__gt=models.F("start")),
                name="shift_ends_after_start",
                violation_error_message="Un poste doit se terminer après son début.",
            ),
            ExclusionConstraint(
                name="exclude_overlapping_shifts",
                expressions=[
                    (TsTzRange("start", "end", RangeBoundary()), RangeOperators.OVERLAPS),
                    ("staff", RangeOperators.EQUAL),
                ],
                violation_error_message="Ce soignant a déjà un poste sur ce créneau.",
                condition=models.Q(end__gt=models.F("start")),
            ),
        ]
        ordering = ["start", "staff__code"]

    def __str__(self) -> str:
        return (
            f"{self.staff.code} : {self.kind} "
            f"du {self.start:%d/%m/%Y %H:%M} au {self.end:%d/%m/%Y %H:%M}"
        )

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

    objects = DayOffRequestQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["staff", "day"], name="unique_day_off_request"),
        ]

    def __str__(self) -> str:
        return f"{self.staff.code} : repos demandé le {self.day:%d/%m/%Y}"

    def to_engine(self) -> engine.DayOffRequest:
        """Convertit la demande de repos enregistrée en une demande de repos du moteur de règles."""

        return engine.DayOffRequest(
            staff_id=self.staff.code,
            day=self.day,
        )
