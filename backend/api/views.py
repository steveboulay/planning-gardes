from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import CheckScheduleSerializer, StaffMemberSerializer, ViolationSerializer
from planning_rules.models import DEFAULT_CONFIG
from planning_rules.rules import check_schedule
from schedules.models import StaffMember


class CheckScheduleView(APIView):
    def post(self, request):
        serializer = CheckScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        violations = check_schedule(
            shifts=serializer.validated_data["shifts"],
            requests=serializer.validated_data["day_off_requests"],
            config=serializer.validated_data.get("config", DEFAULT_CONFIG),
        )
        return Response({"violations": ViolationSerializer(violations, many=True).data})


class StaffMemberListView(ListAPIView):
    queryset = StaffMember.objects.all()
    serializer_class = StaffMemberSerializer
