from django.contrib import admin
from django.urls import path,include
from mini.views import LoginWithCodeView, UserProfileView, HackathonListView, HackathonDatesView
from rest_framework_simplejwt.views import TokenRefreshView,TokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/login_with_code/", LoginWithCodeView.as_view(), name="login_with_code"),
    path("api/profile/", UserProfileView.as_view(), name="user_profile"),
    path("api/token/",TokenObtainPairView.as_view(),name='get_token'),
    path('api/token/refresh/',TokenRefreshView.as_view(),name='refresh'),
    path("api-auth/",include("rest_framework.urls")),
    path("api/hackathons/", HackathonListView.as_view(), name="hackathons_list"),
    path("api/hackathon-dates/", HackathonDatesView.as_view(), name="hackathon_dates"),

]
