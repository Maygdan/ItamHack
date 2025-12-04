from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', required=False)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    experience_years = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'is_telegram_user', 'telegram_id',
            'display_name', 'avatar', 'bio', 'skills', 'experience_months', 'level',
            'level_display', 'experience_years', 'hackathons_participated'
        ]
        read_only_fields = ['is_telegram_user', 'telegram_id', 'level', 'level_display']

    def get_experience_years(self, obj):
        years, months = obj.get_experience_years()
        return f"{years} лет {months} месяцев" if years > 0 else f"{months} месяцев"

class LoginWithCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=8)
