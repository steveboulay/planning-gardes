from rest_framework.response import Response
from rest_framework.views import APIView


class CheckScheduleView(APIView):
    def post(self, request):
        return Response({"violations": []})
