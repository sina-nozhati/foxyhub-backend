from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status


class HealthCheckView(APIView):
    """
    Simple health check view to verify the API is running.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {"status": "ok", "message": "API is running"},
            status=status.HTTP_200_OK
        )

