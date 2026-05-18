import stripe
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.products.models import Product

from .forms import CheckoutForm
from .models import Cart, CartItem, Order, OrderItem, Payment
from .stripe_service import create_checkout_session, verify_webhook


def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


# ============================================================
# Cart pages
# ============================================================


@login_required
def cart_detail(request):
    cart = _get_or_create_cart(request.user)
    return render(request, "cart/cart.html", {"cart": cart})


@login_required
@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get("quantity", 1))

    if quantity < 1:
        messages.error(request, "Invalid quantity")
        return redirect(product.get_absolute_url())

    if hasattr(product, "inventory") and product.inventory.quantity < quantity:
        messages.error(request, f"Only {product.inventory.quantity} in stock")
        return redirect(product.get_absolute_url())

    cart = _get_or_create_cart(request.user)
    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, defaults={"quantity": quantity}
    )
    if not created:
        item.quantity += quantity
        item.save()

    messages.success(request, f"{product.name} added to cart")
    return redirect("cart:detail")


@login_required
@require_POST
def cart_update(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get("quantity", 1))

    if quantity < 1:
        item.delete()
        messages.info(request, "Item removed from cart")
    else:
        if (
            hasattr(item.product, "inventory")
            and item.product.inventory.quantity < quantity
        ):
            messages.error(request, f"Only {item.product.inventory.quantity} in stock")
        else:
            item.quantity = quantity
            item.save()
            messages.success(request, "Cart updated")
    return redirect("cart:detail")


@login_required
@require_POST
def cart_remove(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.info(request, "Item removed from cart")
    return redirect("cart:detail")


# ============================================================
# Checkout
# ============================================================


@login_required
def checkout(request):
    cart = _get_or_create_cart(request.user)
    if not cart.items.exists():
        messages.error(request, "Your cart is empty")
        return redirect("cart:detail")

    initial = {
        "full_name": request.user.full_name,
        "email": request.user.email,
        "phone": request.user.phone,
    }

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.total = cart.total
                order.save()

                for cart_item in cart.items.select_related("product"):
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        product_name=cart_item.product.name,
                        unit_price=cart_item.unit_price,
                        quantity=cart_item.quantity,
                    )

                Payment.objects.create(
                    order=order,
                    amount=order.total,
                    status=Payment.Status.PENDING,
                )

            # Create Stripe Checkout Session and redirect
            try:
                session = create_checkout_session(order, request)
                order.payment.stripe_session_id = session.id
                order.payment.save(update_fields=["stripe_session_id", "updated_at"])
                return redirect(session.url, permanent=False)
            except stripe.error.StripeError as e:
                order.mark_failed()
                messages.error(request, f"Payment error: {e.user_message or str(e)}")
                return redirect("cart:detail")
    else:
        form = CheckoutForm(initial=initial)

    return render(request, "cart/checkout.html", {"cart": cart, "form": form})


@login_required
def checkout_success(request):
    session_id = request.GET.get("session_id")
    order = None
    if session_id:
        payment = Payment.objects.filter(stripe_session_id=session_id).first()
        if payment:
            order = payment.order
    return render(request, "cart/success.html", {"order": order})


@login_required
def checkout_cancel(request):
    order_id = request.GET.get("order_id")
    if order_id:
        Order.objects.filter(
            id=order_id, user=request.user, status=Order.Status.PENDING
        ).update(status=Order.Status.CANCELLED)
    messages.info(request, "Payment cancelled")
    return redirect("cart:detail")


# ============================================================
# Stripe webhook
# ============================================================


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = verify_webhook(payload, sig_header)
    except ValueError, stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    event_type = event["type"]
    data_object = event["data"]["object"]

    if event_type == "checkout.session.completed":
        _handle_session_completed(data_object)
    elif event_type == "checkout.session.expired":
        _handle_session_expired(data_object)

    return HttpResponse(status=200)


def _handle_session_completed(session):
    order_id = session.get("metadata", {}).get("order_id")
    if not order_id:
        return

    try:
        order = Order.objects.select_related("payment").get(id=order_id)
    except Order.DoesNotExist:
        return

    # Idempotency: skip if already processed
    if order.is_paid:
        return

    with transaction.atomic():
        payment = order.payment
        payment.stripe_payment_intent = session.get("payment_intent", "")
        payment.status = Payment.Status.SUCCEEDED
        payment.raw_response = session
        payment.save()

        order.mark_paid()

        # Reduce inventory
        for item in order.items.select_related("product__inventory"):
            inv = getattr(item.product, "inventory", None)
            if inv:
                inv.quantity = max(0, inv.quantity - item.quantity)
                inv.save(update_fields=["quantity", "updated_at"])

        # Clear cart
        cart = Cart.objects.filter(user=order.user).first()
        if cart:
            cart.clear()


def _handle_session_expired(session):
    order_id = session.get("metadata", {}).get("order_id")
    if not order_id:
        return
    Order.objects.filter(id=order_id, status=Order.Status.PENDING).update(
        status=Order.Status.CANCELLED
    )


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related("payment").prefetch_related("items__product"),
        id=order_id,
        user=request.user,
    )
    return render(request, "cart/order_detail.html", {"order": order})
