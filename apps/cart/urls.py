from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_detail, name="detail"),
    path("add/<int:product_id>/", views.cart_add, name="add"),
    path("update/<int:item_id>/", views.cart_update, name="update"),
    path("remove/<int:item_id>/", views.cart_remove, name="remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/success/", views.checkout_success, name="checkout-success"),
    path("checkout/cancel/", views.checkout_cancel, name="checkout-cancel"),
    path("webhook/stripe/", views.stripe_webhook, name="stripe-webhook"),
    path("orders/<int:order_id>/", views.order_detail, name="order-detail"),
]
