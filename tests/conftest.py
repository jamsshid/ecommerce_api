"""Shared fixtures for tests."""

import pytest
from django.test import Client
from rest_framework.test import APIClient

from apps.cart.models import Cart, CartItem
from apps.products.models import Category, Inventory, Product
from apps.users.models import CustomUser


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return CustomUser.objects.create_user(
        email="user@test.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def admin_user(db):
    return CustomUser.objects.create_superuser(
        email="admin@test.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
    )


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def auth_api_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def category(db):
    return Category.objects.create(name="Fruits", slug="fruits")


@pytest.fixture
def product(db, category, user):
    p = Product.objects.create(
        name="Apple",
        slug="apple",
        description="Fresh apple",
        price="50.00",
        discount_price="45.00",
        category=category,
        seller=user,
    )
    Inventory.objects.create(product=p, sku="APL-001", quantity=10)
    return p


@pytest.fixture
def cart_with_item(db, user, product):
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    return cart
