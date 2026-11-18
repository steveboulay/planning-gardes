from datetime import date

from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import (
    CheckScheduleSerializer,
    PeriodSerializer,
    StaffMemberSerializer,
    StoredShiftSerializer,
    ViolationSerializer,
)
from planning_rules.models import DEFAULT_CONFIG
from planning_rules.rules import check_schedule
from schedules.models import DayOffRequest, Shift, ShiftQuerySet, StaffMember


class CheckScheduleView(APIView):
    def post(self, request: Request) -> Response:
        serializer = CheckScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        violations = check_schedule(
            shifts=serializer.validated_data["shifts"],
            requests=serializer.validated_data["day_off_requests"],
            config=serializer.validated_data.get("config", DEFAULT_CONFIG),
        )
        return Response({"violations": ViolationSerializer(violations, many=True).data})


def validated_period(request: Request) -> tuple[date, date]:
    """Valide la période de la chaîne de requête et renvoie son début et sa fin."""

    serializer = PeriodSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data["start"], serializer.validated_data["end"]


class StaffMemberListView(ListAPIView):
    queryset = StaffMember.objects.all()
    serializer_class = StaffMemberSerializer


class ShiftListView(ListAPIView):
    serializer_class = StoredShiftSerializer

    def get_queryset(self) -> ShiftQuerySet:
        start, end = validated_period(self.request)
        return Shift.objects.starting_between(start, end)


class StoredViolationsView(APIView):
    def get(self, request: Request) -> Response:
        start, end = validated_period(request)
        shifts = [shift.to_engine() for shift in Shift.objects.starting_between(start, end)]
        day_off_requests = [
            day_off.to_engine() for day_off in DayOffRequest.objects.between(start, end)
        ]
        violations = check_schedule(shifts=shifts, requests=day_off_requests)
        return Response({"violations": ViolationSerializer(violations, many=True).data})
