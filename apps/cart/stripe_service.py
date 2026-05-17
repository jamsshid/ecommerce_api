import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(order, request):
    """Create a Stripe Checkout Session for the given order."""
    line_items = []
    for item in order.items.all():
        line_items.append(
            {
                "price_data": {
                    "currency": settings.STRIPE_CURRENCY,
                    "product_data": {
                        "name": item.product_name,
                    },
                    "unit_amount": int(item.unit_price * 100),  # cents
                },
                "quantity": item.quantity,
            }
        )

    base_url = settings.SITE_URL.rstrip("/")
    success_url = (
        f"{base_url}/cart/checkout/success/?session_id={{CHECKOUT_SESSION_ID}}"
    )
    cancel_url = f"{base_url}/cart/checkout/cancel/?order_id={order.id}"

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=order.email,
        metadata={
            "order_id": str(order.id),
            "user_id": str(order.user_id),
        },
    )
    return session


def verify_webhook(payload, sig_header):
    """Verify a Stripe webhook event."""
    return stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )
