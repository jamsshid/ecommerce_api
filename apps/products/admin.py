from django.contrib import admin

from .models import Category, Inventory, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "order")


class InventoryInline(admin.StackedInline):
    model = Inventory
    can_delete = False
    fields = ("sku", "quantity", "low_stock_threshold")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active", "created_at")
    list_filter = ("is_active", "parent")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "seller",
        "price",
        "discount_price",
        "is_active",
        "is_featured",
        "created_at",
    )
    list_filter = ("is_active", "is_featured", "category", "created_at")
    search_fields = ("name", "slug", "description", "seller__email")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("category", "seller")
    inlines = [InventoryInline, ProductImageInline]
    readonly_fields = ("created_at", "updated_at")
    view_on_site = True


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("sku", "product", "quantity", "low_stock_threshold", "updated_at")
    search_fields = ("sku", "product__name")
    autocomplete_fields = ("product",)
