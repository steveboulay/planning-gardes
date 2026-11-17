from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import CheckScheduleSerializer


class CheckScheduleView(APIView):
    def post(self, request):
        serializer = CheckScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"violations": []})
