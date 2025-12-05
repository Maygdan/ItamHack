from django.contrib.auth.models import User
from .serializers import LoginWithCodeSerializer, UserProfileSerializer, HackathonSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import LoginCode, UserProfile, Hackathon
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

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
                # Get or create user and profile
                telegram_id = login_code.telegram_id
                user, created = User.objects.get_or_create(username=telegram_id)

                # Always create/update profile for Telegram users
                profile, profile_created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'is_telegram_user': True,
                        'telegram_id': telegram_id,
                        'display_name': user.username  # Default display_name
                    }
                )

                # If profile already existed, make sure it's marked as Telegram user
                if not profile_created:
                    profile.is_telegram_user = True
                    profile.telegram_id = telegram_id
                    profile.save()

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            except LoginCode.DoesNotExist:
                return Response({"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HackathonListView(generics.ListAPIView):
    serializer_class = HackathonSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Hackathon.objects.all()

class HackathonDatesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        hackathons = Hackathon.objects.values_list('start_date', flat=True)
        dates = list(set(str(date) for date in hackathons))  # Преобразовать в строки для JSON
        return Response({'hackathon_dates': dates})
