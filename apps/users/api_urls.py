from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = "users_api"

urlpatterns = [
    path("register/", views.RegisterAPIView.as_view(), name="register"),
    path("login/", views.LoginAPIView.as_view(), name="login"),
    path("logout/", views.LogoutAPIView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("profile/", views.ProfileAPIView.as_view(), name="profile"),
    path(
        "password/change/",
        views.ChangePasswordAPIView.as_view(),
        name="password-change",
    ),
    path("list/", views.UserListAPIView.as_view(), name="list"),
]
