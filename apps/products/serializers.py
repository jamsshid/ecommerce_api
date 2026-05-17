from rest_framework import serializers

from .models import Category, Inventory, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "description", "image", "is_active"]


class InventorySerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)
    is_out_of_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Inventory
        fields = [
            "sku",
            "quantity",
            "low_stock_threshold",
            "is_low_stock",
            "is_out_of_stock",
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "order"]


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""

    category = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    current_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    has_discount = serializers.BooleanField(read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "price",
            "discount_price",
            "current_price",
            "has_discount",
            "discount_percent",
            "category",
            "image",
            "is_featured",
            "in_stock",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    seller = serializers.StringRelatedField(read_only=True)
    inventory = InventorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    current_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    has_discount = serializers.BooleanField(read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "discount_price",
            "current_price",
            "has_discount",
            "discount_percent",
            "category",
            "category_id",
            "seller",
            "image",
            "images",
            "inventory",
            "is_active",
            "is_featured",
            "in_stock",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "seller", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["seller"] = self.context["request"].user
        return super().create(validated_data)
