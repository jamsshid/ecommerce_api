"""Tests for cart, orders and Stripe integration."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse

from apps.cart.models import CartItem, Order, OrderItem, Payment


@pytest.mark.django_db
class TestCartModel:
    def test_cart_total(self, cart_with_item):
        # 2 × 45.00 = 90.00
        assert cart_with_item.total == Decimal("90.00")

    def test_cart_total_items(self, cart_with_item):
        assert cart_with_item.total_items == 2

    def test_clear_cart(self, cart_with_item):
        cart_with_item.clear()
        assert cart_with_item.items.count() == 0


@pytest.mark.django_db
class TestCartViews:
    def test_cart_requires_login(self, client):
        response = client.get(reverse("cart:detail"))
        assert response.status_code == 302

    def test_cart_detail(self, auth_client):
        response = auth_client.get(reverse("cart:detail"))
        assert response.status_code == 200

    def test_add_to_cart(self, auth_client, product):
        response = auth_client.post(
            reverse("cart:add", args=[product.id]),
            {"quantity": 2},
        )
        assert response.status_code == 302
        assert CartItem.objects.filter(product=product).exists()

    def test_add_more_than_stock_blocked(self, auth_client, product):
        auth_client.post(
            reverse("cart:add", args=[product.id]),
            {"quantity": 999},
        )
        assert not CartItem.objects.filter(product=product).exists()

    def test_add_same_product_increments(self, auth_client, product):
        url = reverse("cart:add", args=[product.id])
        auth_client.post(url, {"quantity": 1})
        auth_client.post(url, {"quantity": 2})
        item = CartItem.objects.get(product=product)
        assert item.quantity == 3

    def test_update_cart_item(self, auth_client, cart_with_item):
        item = cart_with_item.items.first()
        response = auth_client.post(
            reverse("cart:update", args=[item.id]),
            {"quantity": 5},
        )
        assert response.status_code == 302
        item.refresh_from_db()
        assert item.quantity == 5

    def test_update_to_zero_removes(self, auth_client, cart_with_item):
        item = cart_with_item.items.first()
        auth_client.post(
            reverse("cart:update", args=[item.id]),
            {"quantity": 0},
        )
        assert not CartItem.objects.filter(id=item.id).exists()

    def test_remove_cart_item(self, auth_client, cart_with_item):
        item = cart_with_item.items.first()
        response = auth_client.post(reverse("cart:remove", args=[item.id]))
        assert response.status_code == 302
        assert not CartItem.objects.filter(id=item.id).exists()


@pytest.mark.django_db
class TestCheckout:
    def test_checkout_requires_login(self, client):
        response = client.get(reverse("cart:checkout"))
        assert response.status_code == 302

    def test_checkout_empty_cart_redirects(self, auth_client):
        response = auth_client.get(reverse("cart:checkout"))
        assert response.status_code == 302

    def test_checkout_page_loads(self, auth_client, cart_with_item):
        response = auth_client.get(reverse("cart:checkout"))
        assert response.status_code == 200

    @patch("apps.cart.views.create_checkout_session")
    def test_checkout_post_creates_order(
        self, mock_stripe, auth_client, cart_with_item, user
    ):
        mock_session = MagicMock()
        mock_session.id = "cs_test_123"
        mock_session.url = "https://stripe.com/test-session"
        mock_stripe.return_value = mock_session

        response = auth_client.post(
            reverse("cart:checkout"),
            {
                "full_name": "Test User",
                "email": user.email,
                "phone": "+998900000000",
                "shipping_address": "Test address",
                "city": "Tashkent",
                "postal_code": "100000",
            },
        )
        assert response.status_code == 302
        assert Order.objects.filter(user=user).exists()
        order = Order.objects.get(user=user)
        assert order.status == Order.Status.PENDING
        assert order.items.count() == 1
        assert order.payment.stripe_session_id == "cs_test_123"


@pytest.mark.django_db
class TestStripeWebhook:
    @patch("apps.cart.views.verify_webhook")
    def test_webhook_session_completed(
        self, mock_verify, client, cart_with_item, user, product
    ):
        # Create order in pending state
        order = Order.objects.create(
            user=user,
            total=Decimal("90.00"),
            full_name="Test",
            email=user.email,
            phone="123",
            shipping_address="addr",
            city="city",
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            unit_price=product.current_price,
            quantity=2,
        )
        Payment.objects.create(order=order, amount=order.total)

        # Mock Stripe webhook event
        mock_verify.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {"order_id": str(order.id)},
                    "payment_intent": "pi_test_123",
                }
            },
        }

        initial_stock = product.inventory.quantity
        response = client.post(
            reverse("cart:stripe-webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=1,v1=test",
        )
        assert response.status_code == 200

        # Order should now be paid
        order.refresh_from_db()
        assert order.status == Order.Status.PAID

        # Payment record updated
        order.payment.refresh_from_db()
        assert order.payment.status == Payment.Status.SUCCEEDED
        assert order.payment.stripe_payment_intent == "pi_test_123"

        # Inventory reduced
        product.inventory.refresh_from_db()
        assert product.inventory.quantity == initial_stock - 2

        # Cart cleared
        assert not CartItem.objects.filter(cart__user=user).exists()

    @patch("apps.cart.views.verify_webhook")
    def test_webhook_idempotent(self, mock_verify, client, user, product):
        order = Order.objects.create(
            user=user,
            total=Decimal("45.00"),
            status=Order.Status.PAID,
            full_name="Test",
            email=user.email,
            phone="123",
            shipping_address="addr",
            city="city",
        )
        Payment.objects.create(order=order, amount=order.total)

        mock_verify.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": {"metadata": {"order_id": str(order.id)}}},
        }

        initial_stock = product.inventory.quantity
        client.post(
            reverse("cart:stripe-webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=1,v1=test",
        )

        # Stock should NOT be reduced a second time
        product.inventory.refresh_from_db()
        assert product.inventory.quantity == initial_stock

    def test_webhook_invalid_signature(self, client):
        response = client.post(
            reverse("cart:stripe-webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="invalid",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestOrderDetail:
    def test_order_detail_view(self, auth_client, user):
        order = Order.objects.create(
            user=user,
            total=Decimal("50.00"),
            full_name="Test",
            email=user.email,
            phone="123",
            shipping_address="addr",
            city="city",
        )
        response = auth_client.get(reverse("cart:order-detail", args=[order.id]))
        assert response.status_code == 200

    def test_order_detail_other_users_blocked(self, auth_client, db):
        from apps.users.models import CustomUser

        other = CustomUser.objects.create_user(email="other@test.com", password="x")
        order = Order.objects.create(
            user=other,
            total=Decimal("50.00"),
            full_name="Other",
            email=other.email,
            phone="123",
            shipping_address="addr",
            city="city",
        )
        response = auth_client.get(reverse("cart:order-detail", args=[order.id]))
        assert response.status_code == 404
