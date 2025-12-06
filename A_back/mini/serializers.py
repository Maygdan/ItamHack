from rest_framework import serializers
from .models import UserProfile, Hackathon, HackathonParticipant, Team, TeamMember, Message

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

class HackathonDetailSerializer(HackathonSerializer):
    class Meta(HackathonSerializer.Meta):
        fields = HackathonSerializer.Meta.fields + ['team_size_min', 'team_size_max', 'partners', 'registration_deadline']

class TeamSerializer(serializers.ModelSerializer):
    captain_username = serializers.CharField(source='captain.username', read_only=True)
    member_count = serializers.SerializerMethodField()
    members_list = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'name', 'captain', 'captain_username', 'member_count', 'members_list', 'size_min', 'size_max', 'is_full']

    def get_member_count(self, obj):
        return obj.members.count()

    def get_members_list(self, obj):
        return [{'username': member.username, 'id': member.id} for member in obj.members.all()]

class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['name', 'hackathon', 'size_min', 'size_max']

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_username', 'receiver', 'receiver_username', 'team', 'team_name', 'message_type', 'status', 'text', 'sent_at']
