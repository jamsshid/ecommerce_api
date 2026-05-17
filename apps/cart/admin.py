from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem, Payment


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("subtotal",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "total_items", "total", "updated_at")
    search_fields = ("user__email",)
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "unit_price", "quantity", "subtotal")
    can_delete = False


class PaymentInline(admin.StackedInline):
    model = Payment
    can_delete = False
    readonly_fields = (
        "stripe_session_id",
        "stripe_payment_intent",
        "amount",
        "currency",
        "status",
        "raw_response",
        "created_at",
        "updated_at",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total", "full_name", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "user__email", "full_name", "email")
    readonly_fields = ("total", "created_at", "updated_at")
    inlines = [OrderItemInline, PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "amount", "currency", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("stripe_session_id", "stripe_payment_intent", "order__id")
    readonly_fields = (
        "order",
        "stripe_session_id",
        "stripe_payment_intent",
        "amount",
        "currency",
        "raw_response",
        "created_at",
        "updated_at",
    )
