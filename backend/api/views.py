from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import CheckScheduleSerializer, ViolationSerializer
from planning_rules.rules import check_schedule


class CheckScheduleView(APIView):
    def post(self, request):
        serializer = CheckScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        violations = check_schedule(shifts=serializer.validated_data["shifts"])
        return Response({"violations": ViolationSerializer(violations, many=True).data})
