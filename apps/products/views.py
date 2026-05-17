from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from rest_framework import filters, generics, permissions

from apps.users.permissions import IsOwnerOrAdmin, ReadOnlyOrAdmin

from .filters import ProductFilter
from .models import Category, Product
from .serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)

# ============================================================
# API Views
# ============================================================


class CategoryListAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrAdmin]


class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrAdmin]
    lookup_field = "slug"


class ProductListAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.filter(is_active=True).select_related(
        "category", "seller", "inventory"
    )
    filterset_class = ProductFilter
    filter_backends = [
        *generics.ListCreateAPIView.filter_backends,
        filters.OrderingFilter,
    ]
    ordering_fields = ["price", "created_at", "name"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductDetailSerializer
        return ProductListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related(
        "category", "seller", "inventory"
    ).prefetch_related("images")
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]


# ============================================================
# Template Views
# ============================================================


def product_list_view(request):
    qs = Product.objects.filter(is_active=True).select_related("category", "inventory")

    # Filters
    category_slug = request.GET.get("category")
    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    search = request.GET.get("q")
    if search:
        qs = qs.filter(name__icontains=search) | qs.filter(
            description__icontains=search
        )

    min_price = request.GET.get("min_price")
    if min_price:
        qs = qs.filter(price__gte=min_price)

    max_price = request.GET.get("max_price")
    if max_price:
        qs = qs.filter(price__lte=max_price)

    sort = request.GET.get("sort", "-created_at")
    if sort in {"price", "-price", "name", "-name", "created_at", "-created_at"}:
        qs = qs.order_by(sort)

    # Pagination
    paginator = Paginator(qs, 12)
    page = request.GET.get("page", 1)
    products = paginator.get_page(page)

    categories = Category.objects.filter(is_active=True, parent__isnull=True)

    context = {
        "products": products,
        "categories": categories,
        "selected_category": category_slug,
        "search_query": search or "",
        "sort": sort,
        "min_price": min_price or "",
        "max_price": max_price or "",
    }
    return render(request, "products/list.html", context)


def product_detail_view(request, slug):
    product = get_object_or_404(
        Product.objects.select_related(
            "category", "seller", "inventory"
        ).prefetch_related("images"),
        slug=slug,
        is_active=True,
    )
    related = (
        Product.objects.filter(category=product.category, is_active=True)
        .exclude(id=product.id)
        .select_related("inventory")[:4]
    )
    return render(
        request,
        "products/detail.html",
        {"product": product, "related_products": related},
    )
