from rest_framework import serializers
from .models import UserProfile, Hackathon

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

class HackathonSerializer(serializers.ModelSerializer):
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    date_range = serializers.SerializerMethodField()

    class Meta:
        model = Hackathon
        fields = [
            'id', 'name', 'start_date', 'start_time', 'end_date', 'date_range', 'category',
            'category_display', 'difficulty', 'difficulty_display', 'max_teams', 'registered_teams', 'required_roles'
        ]

    def get_date_range(self, obj):
        return f"{obj.start_date.strftime('%d.%m')} {obj.start_time.strftime('%H.%M')}"
