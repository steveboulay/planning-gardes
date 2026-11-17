from django.db import models

from planning_rules import models as engine


class StaffMember(models.Model):
    code = models.CharField(max_length=50)
    full_name = models.CharField(max_length=200)


class Shift(models.Model):
    staff = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name="shifts")
    start = models.DateTimeField()
    end = models.DateTimeField()
    kind = models.CharField(
        max_length=4, choices=[(kind.value, kind.value) for kind in engine.ShiftKind]
    )

    def to_engine(self) -> engine.Shift:
        """Convertit le poste enregistré en poste du moteur de règles."""

        return engine.Shift(
            staff_id=self.staff.code,
            start=self.start,
            end=self.end,
            kind=engine.ShiftKind(self.kind),
        )
