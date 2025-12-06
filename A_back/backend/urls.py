from django.contrib import admin
from django.urls import path,include
from mini.views import (
    LoginWithCodeView, UserProfileView, HackathonListView, HackathonDatesView, HackathonDetailView,
    ParticipateHackathonView, CreateTeamView, PotentialMembersView, InviteMemberView,
    AvailableTeamsView, JoinTeamRequestView, MessagesView, RespondMessageView, MyTeamsView, DeleteTeamView
)
from rest_framework_simplejwt.views import TokenRefreshView,TokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/login_with_code/", LoginWithCodeView.as_view(), name="login_with_code"),
    path("api/profile/", UserProfileView.as_view(), name="user_profile"),
    path("api/token/",TokenObtainPairView.as_view(),name='get_token'),
    path('api/token/refresh/',TokenRefreshView.as_view(),name='refresh'),
    path("api-auth/",include("rest_framework.urls")),
    path("api/hackathons/", HackathonListView.as_view(), name="hackathons_list"),
    path("api/hackathons/<int:pk>/", HackathonDetailView.as_view(), name="hackathon_detail"),
    path("api/hackathon-dates/", HackathonDatesView.as_view(), name="hackathon_dates"),
    path("api/hackathons/<int:pk>/participate/", ParticipateHackathonView.as_view(), name="participate_hackathon"),
    path("api/hackathons/<int:pk>/create_team/", CreateTeamView.as_view(), name="create_team"),
    path("api/hackathons/<int:pk>/potential_members/", PotentialMembersView.as_view(), name="potential_members"),
    path("api/teams/<int:team_id>/invite/", InviteMemberView.as_view(), name="invite_member"),
    path("api/hackathons/<int:pk>/available_teams/", AvailableTeamsView.as_view(), name="available_teams"),
    path("api/teams/<int:team_id>/join/", JoinTeamRequestView.as_view(), name="join_team_request"),
    path("api/messages/", MessagesView.as_view(), name="messages"),
    path("api/messages/<int:message_id>/respond/", RespondMessageView.as_view(), name="respond_message"),
    path("api/my_teams/", MyTeamsView.as_view(), name="my_teams"),
    path("api/teams/<int:team_id>/delete/", DeleteTeamView.as_view(), name="delete_team"),

]
