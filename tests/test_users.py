"""Tests for users app."""

import pytest
from django.urls import reverse

from apps.users.models import CustomUser


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = CustomUser.objects.create_user(
            email="new@test.com", password="pass12345"
        )
        assert user.email == "new@test.com"
        assert user.check_password("pass12345")
        assert user.role == CustomUser.Role.CUSTOMER
        assert user.is_active is True

    def test_create_superuser(self):
        admin = CustomUser.objects.create_superuser(
            email="admin@test.com", password="pass12345"
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.role == CustomUser.Role.ADMIN

    def test_email_required(self):
        with pytest.raises(ValueError):
            CustomUser.objects.create_user(email="", password="pass12345")

    def test_full_name_property(self, user):
        assert user.full_name == "Test User"

    def test_full_name_falls_back_to_email(self, db):
        user = CustomUser.objects.create_user(email="x@test.com", password="x")
        assert user.full_name == "x@test.com"


@pytest.mark.django_db
class TestRegisterView:
    def test_get_register_page(self, client):
        response = client.get(reverse("users:register"))
        assert response.status_code == 200

    def test_register_creates_user(self, client):
        response = client.post(
            reverse("users:register"),
            {
                "email": "new@test.com",
                "first_name": "New",
                "last_name": "User",
                "phone": "+998900000000",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            },
        )
        assert response.status_code == 302
        assert CustomUser.objects.filter(email="new@test.com").exists()

    def test_register_password_mismatch(self, client):
        response = client.post(
            reverse("users:register"),
            {
                "email": "x@test.com",
                "first_name": "X",
                "last_name": "Y",
                "password1": "ComplexPass123!",
                "password2": "Different123!",
            },
        )
        assert response.status_code == 200
        assert not CustomUser.objects.filter(email="x@test.com").exists()


@pytest.mark.django_db
class TestLoginView:
    def test_login_success(self, client, user):
        response = client.post(
            reverse("users:login"),
            {
                "email": user.email,
                "password": "testpass123",
            },
        )
        assert response.status_code == 302

    def test_login_wrong_password(self, client, user):
        response = client.post(
            reverse("users:login"),
            {
                "email": user.email,
                "password": "wrongpass",
            },
        )
        assert response.status_code == 200

    def test_profile_requires_login(self, client):
        response = client.get(reverse("users:profile"))
        assert response.status_code == 302

    def test_profile_accessible_when_logged_in(self, auth_client):
        response = auth_client.get(reverse("users:profile"))
        assert response.status_code == 200


@pytest.mark.django_db
class TestUserAPI:
    def test_register_api(self, api_client):
        response = api_client.post(
            "/api/v1/users/register/",
            {
                "email": "api@test.com",
                "first_name": "API",
                "last_name": "User",
                "password": "ComplexPass123!",
                "password2": "ComplexPass123!",
            },
            format="json",
        )
        assert response.status_code == 201
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_api(self, api_client, user):
        response = api_client.post(
            "/api/v1/users/login/",
            {
                "email": user.email,
                "password": "testpass123",
            },
            format="json",
        )
        assert response.status_code == 200
        assert "access" in response.data

    def test_profile_api_requires_auth(self, api_client):
        response = api_client.get("/api/v1/users/profile/")
        assert response.status_code == 401

    def test_profile_api_authenticated(self, auth_api_client, user):
        response = auth_api_client.get("/api/v1/users/profile/")
        assert response.status_code == 200
        assert response.data["email"] == user.email
