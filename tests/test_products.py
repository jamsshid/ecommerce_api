"""Tests for products app."""

import pytest
from django.urls import reverse

from apps.products.models import Category, Product


@pytest.mark.django_db
class TestProductModel:
    def test_create_product(self, category, user):
        p = Product.objects.create(
            name="Banana",
            price="10.00",
            category=category,
            seller=user,
        )
        assert p.slug == "banana"
        assert str(p) == "Banana"

    def test_current_price_with_discount(self, product):
        assert product.current_price == product.discount_price
        assert product.has_discount is True

    def test_discount_percent(self, product):
        # price=50, discount=45 → 10%
        assert product.discount_percent == 10

    def test_no_discount(self, category, user):
        p = Product.objects.create(
            name="Mango",
            price="20.00",
            category=category,
            seller=user,
        )
        assert p.has_discount is False
        assert p.discount_percent == 0
        assert p.current_price == p.price

    def test_in_stock(self, product):
        assert product.in_stock is True

    def test_inventory_low_stock(self, product):
        product.inventory.quantity = 3
        product.inventory.save()
        assert product.inventory.is_low_stock is True

    def test_category_slug_auto(self, db):
        cat = Category.objects.create(name="Electronics")
        assert cat.slug == "electronics"


@pytest.mark.django_db
class TestProductListView:
    def test_list_page_loads(self, client, product):
        response = client.get(reverse("products:list"))
        assert response.status_code == 200
        assert product.name.encode() in response.content

    def test_list_filter_by_category(self, client, product):
        response = client.get(
            reverse("products:list"), {"category": product.category.slug}
        )
        assert response.status_code == 200

    def test_list_search(self, client, product):
        response = client.get(reverse("products:list"), {"q": "Apple"})
        assert response.status_code == 200
        assert product.name.encode() in response.content

    def test_inactive_product_hidden(self, client, product):
        product.is_active = False
        product.save()
        response = client.get(reverse("products:list"))
        assert product.name.encode() not in response.content


@pytest.mark.django_db
class TestProductDetailView:
    def test_detail_page(self, client, product):
        response = client.get(product.get_absolute_url())
        assert response.status_code == 200
        assert product.name.encode() in response.content

    def test_404_for_inactive(self, client, product):
        product.is_active = False
        product.save()
        response = client.get(product.get_absolute_url())
        assert response.status_code == 404


@pytest.mark.django_db
class TestProductAPI:
    def test_list_api(self, api_client, product):
        response = api_client.get("/api/v1/products/")
        assert response.status_code == 200
        assert response.data["count"] >= 1 or len(response.data) >= 1

    def test_detail_api(self, api_client, product):
        response = api_client.get(f"/api/v1/products/{product.slug}/")
        assert response.status_code == 200
        assert response.data["name"] == product.name

    def test_create_requires_auth(self, api_client, category):
        response = api_client.post(
            "/api/v1/products/",
            {
                "name": "New",
                "price": "10.00",
                "category_id": category.id,
            },
            format="json",
        )
        assert response.status_code == 401

    def test_create_product_authenticated(self, auth_api_client, category):
        response = auth_api_client.post(
            "/api/v1/products/",
            {
                "name": "Pear",
                "price": "12.00",
                "category_id": category.id,
            },
            format="json",
        )
        assert response.status_code == 201
        assert Product.objects.filter(name="Pear").exists()
