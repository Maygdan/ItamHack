from django.contrib.auth.models import User
from .serializers import LoginWithCodeSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import LoginCode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

class LoginWithCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginWithCodeSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            try:
                login_code = LoginCode.objects.get(code=code, used=False)
                if login_code.is_expired:
                    return Response({"error": "Code expired"}, status=status.HTTP_400_BAD_REQUEST)
                # Mark code as used
                login_code.used = True
                login_code.save()
                # Get or create user
                telegram_id = login_code.telegram_id
                user, created = User.objects.get_or_create(username=telegram_id)
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            except LoginCode.DoesNotExist:
                return Response({"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
