from decimal import Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField("Name", max_length=150)
    slug = models.SlugField("Slug", max_length=160, unique=True, blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        blank=True,
        null=True,
        verbose_name="Parent category",
    )
    description = models.TextField("Description", blank=True)
    image = models.ImageField("Image", upload_to="categories/", blank=True, null=True)
    is_active = models.BooleanField("Active", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:category", kwargs={"slug": self.slug})


class Product(models.Model):
    name = models.CharField("Name", max_length=200)
    slug = models.SlugField("Slug", max_length=220, unique=True, blank=True)
    description = models.TextField("Description", blank=True)
    price = models.DecimalField(
        "Price", max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    discount_price = models.DecimalField(
        "Discount price",
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Category",
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Seller",
    )
    image = models.ImageField(
        "Main image", upload_to="products/", blank=True, null=True
    )
    is_active = models.BooleanField("Active", default=True)
    is_featured = models.BooleanField("Featured", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"slug": self.slug})

    @property
    def current_price(self) -> Decimal:
        return self.discount_price if self.discount_price else self.price

    @property
    def has_discount(self) -> bool:
        return bool(self.discount_price and self.discount_price < self.price)

    @property
    def discount_percent(self) -> int:
        if not self.has_discount:
            return 0
        return int(round((1 - self.discount_price / self.price) * 100))

    @property
    def in_stock(self) -> bool:
        return hasattr(self, "inventory") and self.inventory.quantity > 0


class ProductImage(models.Model):
    """Extra gallery images for a product."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField("Image", upload_to="products/")
    alt_text = models.CharField("Alt text", max_length=200, blank=True)
    order = models.PositiveSmallIntegerField("Order", default=0)

    class Meta:
        verbose_name = "Product image"
        verbose_name_plural = "Product images"
        ordering = ["order", "id"]

    def __str__(self):
        return f"Image for {self.product.name}"


class Inventory(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="inventory"
    )
    sku = models.CharField("SKU", max_length=64, unique=True)
    quantity = models.PositiveIntegerField("Quantity", default=0)
    low_stock_threshold = models.PositiveIntegerField("Low stock threshold", default=5)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Inventory"
        verbose_name_plural = "Inventories"

    def __str__(self):
        return f"{self.sku} — {self.quantity} pcs"

    @property
    def is_low_stock(self) -> bool:
        return 0 < self.quantity <= self.low_stock_threshold

    @property
    def is_out_of_stock(self) -> bool:
        return self.quantity == 0