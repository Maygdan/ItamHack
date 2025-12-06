from django.contrib.auth.models import User
from .serializers import LoginWithCodeSerializer, UserProfileSerializer, HackathonSerializer, HackathonDetailSerializer, TeamSerializer, TeamCreateSerializer, MessageSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import LoginCode, UserProfile, Hackathon, HackathonParticipant, Team, TeamMember, Message
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from django.db.models import Q

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

class HackathonDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            hackathon = Hackathon.objects.get(pk=pk)
            teams = Team.objects.filter(hackathon=hackathon)
            serializer = HackathonDetailSerializer(hackathon)
            team_serializer = TeamSerializer(teams, many=True)
            return Response({
                'hackathon': serializer.data,
                'teams': team_serializer.data
            })
        except Hackathon.DoesNotExist:
            return Response({'error': 'Хакатон не найден'}, status=404)

# Регистрация на хакатон
class ParticipateHackathonView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            hackathon = Hackathon.objects.get(pk=pk)
            if not hackathon.is_registration_open():
                return Response({'error': 'Регистрация закрыта'}, status=status.HTTP_400_BAD_REQUEST)
            participant, created = HackathonParticipant.objects.get_or_create(
                user=request.user, hackathon=hackathon, defaults={'status': 'active'}
            )
            if not created:
                return Response({'message': 'Вы уже участвуете в этом хакатоне'}, status=status.HTTP_200_OK)
            return Response({'message': 'Вы зарегистрированы на участие в хакатоне'}, status=status.HTTP_201_CREATED)
        except Hackathon.DoesNotExist:
            return Response({'error': 'Хакатон не найден'}, status=404)

# Создание команды
class CreateTeamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            hackathon = Hackathon.objects.get(pk=pk)
            if not hackathon.is_registration_open():
                return Response({'error': 'Регистрация закрыта'}, status=status.HTTP_400_BAD_REQUEST)
            # Проверить, что пользователь участвует
            if not HackathonParticipant.objects.filter(user=request.user, hackathon=hackathon).exists():
                return Response({'error': 'Вы должны сначала принять участие'}, status=status.HTTP_400_BAD_REQUEST)
            # Проверить, что пользователь не в другой команде
            if TeamMember.objects.filter(
                user=request.user,
                team__hackathon=hackathon,
                status__in=['joined', 'invited']
            ).exists():
                return Response({'error': 'Вы уже в команде'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = TeamCreateSerializer(data=dict(request.data, hackathon=hackathon.id, captain=request.user.id))
            if serializer.is_valid():
                team = serializer.save(captain=request.user)
                # Добавить капитана в members
                TeamMember.objects.create(team=team, user=request.user, status='joined')
                team.save()  # Обновить is_full если нужно
                # Обновить зарегистрированные команды
                from django.db.models import Count
                hackathon.teams_count = hackathon.team_set.count()
                hackathon.save()  # Но лучше field
                # Или прямо из views
                hackathon.registered_teams = Team.objects.filter(hackathon=hackathon).count()
                hackathon.save()
                return Response(TeamSerializer(team).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Hackathon.DoesNotExist:
            return Response({'error': 'Хакатон не найден'}, status=404)

# Список потенциальных участников для приглашений (участники не в командах)
class PotentialMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            hackathon = Hackathon.objects.get(pk=pk)
            # Участники хакатона
            participants = HackathonParticipant.objects.filter(
                hackathon=hackathon,
                status='active'
            ).exclude(user=request.user)  # Исключить себя
            # Исключить тех, кто уже в командах или приглашен
            members_in_teams = TeamMember.objects.filter(
                team__hackathon=hackathon,
                status__in=['joined', 'invited']
            ).values_list('user', flat=True)
            available = participants.exclude(user__in=members_in_teams)
            profiles = [p.user.profile for p in available]
            serializer = UserProfileSerializer(profiles, many=True)
            return Response(serializer.data)
        except Hackathon.DoesNotExist:
            return Response({'error': 'Хакатон не найден'}, status=404)

# Отправить приглашение
class InviteMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id):
        try:
            team = Team.objects.get(pk=team_id, captain=request.user)
            user_id = request.data.get('user_id')
            user = User.objects.get(pk=user_id)
            if TeamMember.objects.filter(team=team, user=user).exists():
                return Response({'error': 'Пользователь уже в команде'}, status=status.HTTP_400_BAD_REQUEST)
            if team.members.count() >= team.size_max:
                return Response({'error': 'Команда полна'}, status=status.HTTP_400_BAD_REQUEST)
            message_text = f"Вас приглашают в команду '{team.name}'. Желаете вступить?"
            Message.objects.create(
                sender=request.user,
                receiver=user,
                team=team,
                message_type='team_invite',
                text=message_text
            )
            TeamMember.objects.create(team=team, user=user, status='invited')
            return Response({'message': 'Приглашение отправлено'})
        except Team.DoesNotExist:
            return Response({'error': 'Команда не найдена или не ваша'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_400_BAD_REQUEST)

# Доступные команды для присоединения
class AvailableTeamsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            hackathon = Hackathon.objects.get(pk=pk)
            teams = Team.objects.filter(hackathon=hackathon, is_full=False).exclude(captain=request.user)
            serializer = TeamSerializer(teams, many=True)
            return Response(serializer.data)
        except Hackathon.DoesNotExist:
            return Response({'error': 'Хакатон не найден'}, status=404)

# Отправить запрос на присоединение
class JoinTeamRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id):
        try:
            team = Team.objects.get(pk=team_id, is_full=False)
            if HackathonParticipant.objects.filter(user=request.user, hackathon=team.hackathon).exists():
                return Response({'error': 'Вы должны сначала принять участие'}, status=status.HTTP_400_BAD_REQUEST)
            if TeamMember.objects.filter(
                user=request.user,
                team__hackathon=team.hackathon,
                status__in=['joined', 'invited']
            ).exists():
                return Response({'error': 'Вы уже в команде или приглашены'}, status=status.HTTP_400_BAD_REQUEST)
            message_text = f"В вашу команду '{team.name}' хочет присоединиться {request.user.username}. Принять?"
            Message.objects.create(
                sender=request.user,
                receiver=team.captain,
                team=team,
                message_type='join_request',
                text=message_text
            )
            return Response({'message': 'Запрос на присоединение отправлен'})
        except Team.DoesNotExist:
            return Response({'error': 'Команда не найдена или полна'}, status=status.HTTP_404_NOT_FOUND)

# Сообщения пользователя
class MessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        messages = Message.objects.filter(
            Q(receiver=request.user) | Q(sender=request.user)
        ).order_by('-sent_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

# Принять/отклонить сообщение
class RespondMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, message_id):
        action = request.data.get('action')  # 'accept' or 'decline'
        try:
            message = Message.objects.get(pk=message_id, receiver=request.user)
            if message.status != 'pending':
                return Response({'error': 'Сообщение уже обработано'}, status=status.HTTP_400_BAD_REQUEST)
            if action == 'accept':
                if message.message_type == 'team_invite':
                    if message.team.members.count() >= message.team.size_max:
                        return Response({'error': 'Команда полна'}, status=status.HTTP_400_BAD_REQUEST)
                    TeamMember.objects.filter(team=message.team, user=request.user).update(status='joined')
                elif message.message_type == 'join_request':
                    if message.team.members.count() >= message.team.size_max:
                        return Response({'error': 'Команда полна'}, status=status.HTTP_400_BAD_REQUEST)
                    TeamMember.objects.create(team=message.team, user=message.sender, status='joined')
                message.status = 'accepted'
            elif action == 'decline':
                if message.message_type == 'team_invite':
                    TeamMember.objects.filter(team=message.team, user=request.user).delete()
                message.status = 'declined'
            else:
                return Response({'error': 'Неверное действие'}, status=status.HTTP_400_BAD_REQUEST)
            message.save()
            # Обновить is_full команды
            team = message.team
            team.is_full = team.members.count() >= team.size_max
            team.save()
            # Обновить зарегистрированные команды хакатона
            team.hackathon.registered_teams = Team.objects.filter(hackathon=team.hackathon, is_full=True).count()
            team.hackathon.save()
            return Response({'message': f'Запрос {action}ed'})
        except Message.DoesNotExist:
            return Response({'error': 'Сообщение не найдено'}, status=status.HTTP_404_NOT_FOUND)

# Мои команды
class MyTeamsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Команды, где пользователь капитан или член
        teams = Team.objects.filter(
            Q(captain=request.user) | Q(teammember__user=request.user, teammember__status='joined')
        ).distinct()
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)

# Удалить команду (только капитан)
class DeleteTeamView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, team_id):
        try:
            team = Team.objects.get(pk=team_id, captain=request.user)
            team.delete()
            # Обновить registered_teams хакатона
            team.hackathon.registered_teams = Team.objects.filter(hackathon=team.hackathon).count()
            team.hackathon.save()
            return Response({'message': 'Команда удалена'})
        except Team.DoesNotExist:
            return Response({'error': 'Команда не найдена или не ваша'}, status=status.HTTP_404_NOT_FOUND)
