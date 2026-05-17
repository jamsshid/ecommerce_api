from django.contrib import messages
from django.contrib.auth import login as django_login, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import LoginForm, ProfileForm, RegisterForm
from .models import CustomUser
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)

class RegisterAPIView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token need!"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            RefreshToken(refresh_token).blacklist()
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "Logged out"}, status=status.HTTP_205_RESET_CONTENT
        )


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordAPIView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password changed successfully!"}, status=status.HTTP_200_OK)


class UserListAPIView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


# ============================================================
# Template Views
# ============================================================


def register_view(request):
    if request.user.is_authenticated:
        return redirect("users:profile")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            django_login(request, user)
            messages.success(request, "Your account has been created successfully!")
            return redirect("users:profile")
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("users:profile")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            django_login(request, user)
            messages.success(request, f"Welcome back, {user.full_name}!")
            return redirect(request.GET.get("next") or "users:profile")
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request):
    django_logout(request)
    messages.info(request, "You have been logged out")
    return redirect("users:login")


@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect("users:profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "users/profile.html", {"form": form})
